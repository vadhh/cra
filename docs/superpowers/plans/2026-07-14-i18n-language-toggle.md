# EN/ID Frontend Language Toggle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a persistent EN/ID language toggle to all six `ldv-frontend/*.html` pages that translates static UI chrome (nav, buttons, headings, labels, tooltips) instantly, client-side, with no backend changes.

**Architecture:** One shared `ldv-frontend/i18n.js` holds a flat `{en: {...}, id: {...}}` dictionary and three primitives — `applyLang()` (walks `[data-i18n]`/`[data-i18n-placeholder]` elements and swaps text), `setLang()`/`toggleLang()` (persist to `localStorage` under `ldv_lang`), and `t(key)` (for Alpine `x-text` expressions that need the current language reactively). A small `Alpine.store('lang', ...)` makes Alpine re-evaluate `x-text` expressions that call `i18n.t()` when the language flips. Each page loads `i18n.js`, gets a fixed-position `EN|ID` toggle pill, and has its static strings tagged with `data-i18n` keys.

**Tech Stack:** Vanilla JS (no new dependencies), existing Alpine.js 3.15 (already CDN-loaded on every page), Node (builtin `fs`/`path`/`Function` only) for the offline dictionary self-check.

## Global Constraints

- No new npm/CDN dependencies — pure vanilla JS plus the Alpine.js instance already on each page.
- `localStorage` key is exactly `ldv_lang`; values `"en"` or `"id"`; unrecognized/missing → default `"en"`.
- Missing translation key → keep the literal English text already in the DOM (never blank, never `undefined`).
- Only static UI chrome is tagged (`data-i18n`) or routed through `i18n.t()` (Alpine-bound dynamic strings). Content sourced from the API at request time (analysis results, red flags, clause guidance, user/org records) is never touched.
- Key naming convention: `<page>.<section>.<element>`, e.g. `index.nav.new_analysis`, `login.form.email_label`. Shared chrome (the admin/citations sidebar, which is byte-for-byte identical markup) uses a shared `nav.sidebar.*` namespace instead of per-page duplicates.
- No backend/API changes of any kind.

---

### Task 1: i18n engine + offline dictionary self-check

**Files:**
- Create: `ldv-frontend/i18n.js`
- Create: `ldv-frontend/i18n.selfcheck.js`

**Interfaces:**
- Produces (consumed by every later task):
  - `window.i18n.getLang(): "en" | "id"`
  - `window.i18n.setLang(lang: "en"|"id"): void` — persists + re-applies
  - `window.i18n.toggleLang(): void` — flips en↔id
  - `window.i18n.t(key: string): string` — dictionary lookup with EN fallback, for use inside Alpine expressions
  - `window.i18n.applyLang(): void` — re-runs the DOM tagging pass (also called automatically on `DOMContentLoaded` and by `setLang`)
  - `window.i18n.DICT: {en: Record<string,string>, id: Record<string,string>}` — the dictionary object every later task adds keys to
  - `Alpine.store('lang')` — reactive current-language string, for `x-text` expressions that need to re-run when language changes (see Task 5 for a worked example)
  - `data-lang-toggle` attribute contract: any element with this attribute gets its `textContent` set to the *target* language code (`"ID"` when currently English, `"EN"` when currently Indonesian) by `applyLang()`.

- [ ] **Step 1: Write `ldv-frontend/i18n.js`**

```js
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
```

- [ ] **Step 2: Write `ldv-frontend/i18n.selfcheck.js`**

```js
// Run: node ldv-frontend/i18n.selfcheck.js
// Asserts every DICT key in i18n.js exists in both `en` and `id`.
// Pure Node — requires i18n.js directly (no eval / new Function / string
// interpolation of file contents; i18n.js guards its browser-only globals
// so it's safe to require() outside a browser).
const { DICT } = require("./i18n.js");

const enKeys = new Set(Object.keys(DICT.en));
const idKeys = new Set(Object.keys(DICT.id));

const missingInId = [...enKeys].filter(function (k) { return !idKeys.has(k); });
const missingInEn = [...idKeys].filter(function (k) { return !enKeys.has(k); });

if (missingInId.length || missingInEn.length) {
  if (missingInId.length) console.error("Missing Indonesian translation for:", missingInId);
  if (missingInEn.length) console.error("Missing English translation for:", missingInEn);
  process.exit(1);
}

console.log("OK: " + enKeys.size + " keys, EN/ID parity confirmed.");
```

- [ ] **Step 3: Run the self-check to verify it passes on the seed dictionary**

Run: `node ldv-frontend/i18n.selfcheck.js`
Expected: `OK: 6 keys, EN/ID parity confirmed.`

- [ ] **Step 4: Break parity on purpose to verify the self-check actually catches drift**

Temporarily add `"nav.temp_test": "x"` to `DICT.en` only in `ldv-frontend/i18n.js`, run the command again.
Expected: exits non-zero, prints `Missing Indonesian translation for: [ 'nav.temp_test' ]`.
Then remove the temporary key.

- [ ] **Step 5: Commit**

```bash
git add ldv-frontend/i18n.js ldv-frontend/i18n.selfcheck.js
git commit -m "feat: add i18n engine and EN/ID dictionary self-check"
```

---

### Task 2: Wire the toggle into `index.html` and translate its chrome

**Files:**
- Modify: `ldv-frontend/index.html:8-16` (head scripts), `:169` (body open), `:172-195` (header/nav)

**Interfaces:**
- Consumes: `window.i18n` from Task 1 (`i18n.js` must be loaded before `DOMContentLoaded`).
- Produces: `index.*` dictionary keys other tasks don't depend on (index.html has no shared chrome with other pages besides the `nav.*`/`brand.name` keys already seeded in Task 1).

- [ ] **Step 1: Load `i18n.js` in `<head>`**

In `ldv-frontend/index.html`, right after the Alpine.js `<script defer ...>` tag (currently line 9), add:

```html
  <script defer src="i18n.js"></script>
```

- [ ] **Step 2: Add the toggle button right after `<body ...>`**

Current line 169:
```html
<body class="selection:bg-primary selection:text-on-primary min-h-screen flex flex-col justify-between" x-data="uploadApp()" x-init="init()">
```

Insert immediately after it:

```html
  <button type="button" data-lang-toggle onclick="i18n.toggleLang()"
          class="fixed top-3 right-3 z-[60] px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider border border-primary/40 bg-surface-container/90 text-primary hover:bg-primary hover:text-on-primary transition-colors backdrop-blur-sm"
          aria-label="Toggle language / Ganti bahasa">ID</button>
```

- [ ] **Step 3: Tag the header/nav (worked example) — replace lines 172-195**

Before:
```html
      <span class="font-editorial text-2xl text-primary tracking-tight">Sydeco CRA</span>
    </div>
    <nav class="hidden md:flex items-center gap-8">
      <a class="text-primary font-bold border-b-2 border-primary pb-1 font-label-md text-label-md" href="/">New Analysis</a>
      <a class="text-on-surface-variant font-medium hover:text-primary transition-colors duration-300 font-label-md text-label-md" href="/admin">Dashboard</a>
      <a class="text-on-surface-variant font-medium hover:text-primary transition-colors duration-300 font-label-md text-label-md" href="/citations">Citation Library</a>
    </nav>
    <div class="flex items-center gap-6">
      <template x-if="loggedIn">
        <a href="/logout" class="gold-button px-6 py-2.5 rounded-md text-on-primary font-label-md text-label-md font-bold uppercase tracking-wider" style="text-decoration:none;">Secure Logout</a>
      </template>
      <template x-if="!loggedIn">
        <a href="/login" class="gold-button px-6 py-2.5 rounded-md text-on-primary font-label-md text-label-md font-bold uppercase tracking-wider" style="text-decoration:none;">Sign In</a>
      </template>
    </div>
```

After:
```html
      <span class="font-editorial text-2xl text-primary tracking-tight" data-i18n="brand.name">Sydeco CRA</span>
    </div>
    <nav class="hidden md:flex items-center gap-8">
      <a class="text-primary font-bold border-b-2 border-primary pb-1 font-label-md text-label-md" href="/" data-i18n="nav.new_analysis">New Analysis</a>
      <a class="text-on-surface-variant font-medium hover:text-primary transition-colors duration-300 font-label-md text-label-md" href="/admin" data-i18n="nav.dashboard">Dashboard</a>
      <a class="text-on-surface-variant font-medium hover:text-primary transition-colors duration-300 font-label-md text-label-md" href="/citations" data-i18n="nav.citation_library">Citation Library</a>
    </nav>
    <div class="flex items-center gap-6">
      <template x-if="loggedIn">
        <a href="/logout" class="gold-button px-6 py-2.5 rounded-md text-on-primary font-label-md text-label-md font-bold uppercase tracking-wider" style="text-decoration:none;" data-i18n="nav.secure_logout">Secure Logout</a>
      </template>
      <template x-if="!loggedIn">
        <a href="/login" class="gold-button px-6 py-2.5 rounded-md text-on-primary font-label-md text-label-md font-bold uppercase tracking-wider" style="text-decoration:none;" data-i18n="nav.sign_in">Sign In</a>
      </template>
    </div>
```

(No new dictionary keys needed here — `nav.*`/`brand.name` were seeded in Task 1.)

- [ ] **Step 4: Tag the rest of `index.html`'s static strings**

Read through the remainder of the file (the MFA warning banner, the 5-step stepper labels, upload panel copy, buttons, empty-states, footer). For each static text node or attribute that is literal English (not `x-text`-bound to app state), apply the same pattern as Step 3:
- Add `data-i18n="index.<section>.<element>"` to the element, keeping its existing English text as-is (that text is the fallback).
- Add matching `"index.<section>.<element>": "..."` entries to both `DICT.en` and `DICT.id` in `ldv-frontend/i18n.js`.
- For any element whose text is set by an Alpine expression (`x-text="someExpr"`) rather than being literal — e.g. the MFA warning banner's dynamic parts, if any — leave a note and handle it the same way Task 5 Step 4 demonstrates (`i18n.t()` + `$store.lang`), don't force it into `data-i18n`.

Do not tag or translate anything driven by `x-text` bound to API response data (contract analysis results, filenames, uploaded document content) — none of that appears until Task 3 territory in `result.html`, so `index.html` itself is entirely static chrome plus form controls.

- [ ] **Step 5: Verify dictionary parity**

Run: `node ldv-frontend/i18n.selfcheck.js`
Expected: `OK: N keys, EN/ID parity confirmed.` (no missing-translation errors)

- [ ] **Step 6: Manual browser verification**

```bash
cd ldv-backend && FLASK_APP=app.py python3 -m flask run --port 5000
```

Open `http://127.0.0.1:5000/` in a browser. Click the `ID` pill top-right — confirm every tagged string switches to Indonesian instantly (no reload), the button now reads `EN`, and clicking it again reverts to English. Reload the page — confirm the language choice persisted (still shows Indonesian if that's where you left it).

- [ ] **Step 7: Commit**

```bash
git add ldv-frontend/index.html ldv-frontend/i18n.js
git commit -m "feat: add EN/ID language toggle to index.html"
```

---

### Task 3: Wire the toggle into `result.html` and translate its chrome

**Files:**
- Modify: `ldv-frontend/result.html` (head scripts near the existing Alpine `<script>` tag, `:579` body open, `:583-604` header/nav, plus the rest of the report UI's static chrome)

**Interfaces:**
- Consumes: `window.i18n` from Task 1.
- Produces: `result.*` keys. Reuses `nav.*`/`brand.name` from Task 1.

- [ ] **Step 1: Load `i18n.js` in `<head>`** (same pattern as Task 2 Step 1 — add `<script defer src="i18n.js"></script>` next to the Alpine script tag).

- [ ] **Step 2: Add the toggle button right after `<body ...>` (line 579)** — identical snippet to Task 2 Step 2.

- [ ] **Step 3: Tag the header/nav (worked example) — replace lines 590-603**

Before:
```html
        <a class="font-editorial text-xl text-primary tracking-tight" href="/" style="text-decoration:none;">Sydeco CRA</a>
      </div>
      <nav class="hidden md:flex items-center gap-6 text-sm">
        <a class="text-on-surface-variant hover:text-primary transition-colors font-medium text-sm" href="/" style="text-decoration:none;">New Analysis</a>
        <a class="text-on-surface-variant hover:text-primary transition-colors font-medium text-sm" href="/admin" style="text-decoration:none;">Dashboard</a>
        <a class="text-on-surface-variant hover:text-primary transition-colors font-medium text-sm" href="/citations" style="text-decoration:none;">Citation Library</a>
      </nav>
      <div class="flex items-center gap-6">
        <a href="/logout" class="text-on-surface-variant hover:text-primary transition-colors text-xs font-bold uppercase tracking-wider" style="text-decoration:none;">Secure Logout</a>
      </div>
```

After:
```html
        <a class="font-editorial text-xl text-primary tracking-tight" href="/" style="text-decoration:none;" data-i18n="brand.name">Sydeco CRA</a>
      </div>
      <nav class="hidden md:flex items-center gap-6 text-sm">
        <a class="text-on-surface-variant hover:text-primary transition-colors font-medium text-sm" href="/" style="text-decoration:none;" data-i18n="nav.new_analysis">New Analysis</a>
        <a class="text-on-surface-variant hover:text-primary transition-colors font-medium text-sm" href="/admin" style="text-decoration:none;" data-i18n="nav.dashboard">Dashboard</a>
        <a class="text-on-surface-variant hover:text-primary transition-colors font-medium text-sm" href="/citations" style="text-decoration:none;" data-i18n="nav.citation_library">Citation Library</a>
      </nav>
      <div class="flex items-center gap-6">
        <a href="/logout" class="text-on-surface-variant hover:text-primary transition-colors text-xs font-bold uppercase tracking-wider" style="text-decoration:none;" data-i18n="nav.secure_logout">Secure Logout</a>
      </div>
```

- [ ] **Step 4: Tag the loading/error/processing state chrome (worked example) — lines 606-628**

Before:
```html
      <p class="font-body text-sm mt-3 text-on-surface-variant">Decrypting and loading assessment data…</p>
    </div>

    <!-- Error State -->
    <div x-show="!loading && errorMsg" style="display:none;" class="max-w-xl mx-auto py-12">
      <div class="bg-red-950/20 border border-red-500/30 rounded p-8 text-center space-y-6">
        <h2 class="font-editorial text-2xl text-red-400">Assessment Error</h2>
        <p class="font-body text-on-surface-variant text-sm" x-text="errorMsg"></p>
        <a href="/" class="btn btn-primary inline-flex">← Run New Analysis</a>
      </div>
    </div>

    <!-- In-Progress Processing State -->
    <div x-show="!loading && !errorMsg && isProcessing" style="display:none;" class="max-w-xl mx-auto py-12 flex flex-col items-center py-6 text-center space-y-8">
      <div class="relative flex items-center justify-center">
        <div class="w-24 h-24 rounded-full border-4 border-primary/20 border-t-primary animate-spin"></div>
        <span class="material-symbols-outlined text-primary text-[36px] absolute">sync_saved_locally</span>
      </div>
      <div class="space-y-2">
        <h3 class="font-editorial text-2xl text-primary">Sovereign Pipeline Processing…</h3>
```

After (note: `errorMsg` on line with `x-text="errorMsg"` is API-sourced — left untouched; only the literal strings around it are tagged):
```html
      <p class="font-body text-sm mt-3 text-on-surface-variant" data-i18n="result.loading.message">Decrypting and loading assessment data…</p>
    </div>

    <!-- Error State -->
    <div x-show="!loading && errorMsg" style="display:none;" class="max-w-xl mx-auto py-12">
      <div class="bg-red-950/20 border border-red-500/30 rounded p-8 text-center space-y-6">
        <h2 class="font-editorial text-2xl text-red-400" data-i18n="result.error.title">Assessment Error</h2>
        <p class="font-body text-on-surface-variant text-sm" x-text="errorMsg"></p>
        <a href="/" class="btn btn-primary inline-flex" data-i18n="result.error.retry_link">← Run New Analysis</a>
      </div>
    </div>

    <!-- In-Progress Processing State -->
    <div x-show="!loading && !errorMsg && isProcessing" style="display:none;" class="max-w-xl mx-auto py-12 flex flex-col items-center py-6 text-center space-y-8">
      <div class="relative flex items-center justify-center">
        <div class="w-24 h-24 rounded-full border-4 border-primary/20 border-t-primary animate-spin"></div>
        <span class="material-symbols-outlined text-primary text-[36px] absolute">sync_saved_locally</span>
      </div>
      <div class="space-y-2">
        <h3 class="font-editorial text-2xl text-primary" data-i18n="result.processing.title">Sovereign Pipeline Processing…</h3>
```

Add to `DICT` in `i18n.js`:
```js
// en
"result.loading.message": "Decrypting and loading assessment data…",
"result.error.title": "Assessment Error",
"result.error.retry_link": "← Run New Analysis",
"result.processing.title": "Sovereign Pipeline Processing…",
// id
"result.loading.message": "Mendekripsi dan memuat data penilaian…",
"result.error.title": "Kesalahan Penilaian",
"result.error.retry_link": "← Jalankan Analisis Baru",
"result.processing.title": "Pipeline Berdaulat Sedang Diproses…",
```

- [ ] **Step 5: Tag the rest of `result.html`'s static chrome**

Same process as Task 2 Step 4: walk the remaining report UI (section headings like "Risk Score", "Red Flags", "Clause Presence", table column headers, button labels, tooltips, empty-states) and tag every literal string with `result.<section>.<element>` keys, adding both `en`/`id` entries to `i18n.js`. Leave every `x-text`/`x-html` binding that renders analysis data (risk scores, clause names pulled from the API, citation text, red-flag descriptions) completely untouched — those come from the backend in the document's own language per the design spec and are explicitly out of scope.

- [ ] **Step 6: Verify dictionary parity**

Run: `node ldv-frontend/i18n.selfcheck.js`
Expected: `OK: N keys, EN/ID parity confirmed.`

- [ ] **Step 7: Manual browser verification**

With the Flask dev server running, upload a test contract from `/`, land on `/result`, toggle the language pill. Confirm all chrome (headings, buttons, section labels) switches instantly while the actual analysis findings (red flags, clause text) stay exactly as returned by the API. Reload — confirm persistence.

- [ ] **Step 8: Commit**

```bash
git add ldv-frontend/result.html ldv-frontend/i18n.js
git commit -m "feat: add EN/ID language toggle to result.html"
```

---

### Task 4: Wire the toggle into `login.html` and translate its chrome

**Files:**
- Modify: `ldv-frontend/login.html` (head scripts, `:134` body open, `:142-152` branding header, `:159-162` login form header, plus the rest of the auth/MFA flow screens)

**Interfaces:**
- Consumes: `window.i18n` from Task 1.
- Produces: `login.*` keys.

- [ ] **Step 1: Load `i18n.js` in `<head>`** — same pattern as Task 2 Step 1.

- [ ] **Step 2: Add the toggle button right after `<body ...>` (line 134)** — identical snippet to Task 2 Step 2. (`login.html` has no persistent top navbar, so the fixed-position button is the only viable placement — matches the design spec's reasoning.)

- [ ] **Step 3: Tag the branding header and login form header (worked example) — lines 142-162**

Before:
```html
      <h1 class="font-display text-5xl text-primary tracking-tight">Access Gate</h1>
      <p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-[0.3em] mt-3 font-semibold">Sovereign Intelligence Protocol</p>
    </div>

    <!-- State 1: Login Form (Email & Password) -->
    <section class="obsidian-panel shadow-3 w-full max-w-md p-10 rounded-lg relative overflow-hidden" x-show="state === 'login'" x-transition>
      <div class="space-y-8 relative z-10">
        <header>
          <h2 class="font-display text-2xl text-on-surface">Secure Identity Verification</h2>
          <p class="text-on-surface-variant mt-1 opacity-80 text-sm">Authorized personnel only.</p>
        </header>

        <form class="space-y-6" @submit.prevent="submitLogin()">
          <!-- Email Input -->
          <div class="space-y-2">
            <label class="font-label-md text-label-sm text-on-surface-variant flex items-center gap-2 uppercase tracking-widest" for="email">
              <span class="material-symbols-outlined text-[18px]">mail</span>
              Institutional Email
            </label>
            <input class="w-full bg-surface-container-lowest border border-outline-variant/30 text-on-surface px-4 py-3.5 rounded focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all text-sm placeholder:text-on-surface/20"
                   id="email" type="email" x-model="email" placeholder="name@sydeco.legal" required autocomplete="email"/>
          </div>
```

After:
```html
      <h1 class="font-display text-5xl text-primary tracking-tight" data-i18n="login.brand.title">Access Gate</h1>
      <p class="font-label-md text-label-md text-on-surface-variant uppercase tracking-[0.3em] mt-3 font-semibold" data-i18n="login.brand.subtitle">Sovereign Intelligence Protocol</p>
    </div>

    <!-- State 1: Login Form (Email & Password) -->
    <section class="obsidian-panel shadow-3 w-full max-w-md p-10 rounded-lg relative overflow-hidden" x-show="state === 'login'" x-transition>
      <div class="space-y-8 relative z-10">
        <header>
          <h2 class="font-display text-2xl text-on-surface" data-i18n="login.form.title">Secure Identity Verification</h2>
          <p class="text-on-surface-variant mt-1 opacity-80 text-sm" data-i18n="login.form.subtitle">Authorized personnel only.</p>
        </header>

        <form class="space-y-6" @submit.prevent="submitLogin()">
          <!-- Email Input -->
          <div class="space-y-2">
            <label class="font-label-md text-label-sm text-on-surface-variant flex items-center gap-2 uppercase tracking-widest" for="email">
              <span class="material-symbols-outlined text-[18px]">mail</span>
              <span data-i18n="login.form.email_label">Institutional Email</span>
            </label>
            <input class="w-full bg-surface-container-lowest border border-outline-variant/30 text-on-surface px-4 py-3.5 rounded focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all text-sm placeholder:text-on-surface/20"
                   id="email" type="email" x-model="email" placeholder="name@sydeco.legal" required autocomplete="email" data-i18n-placeholder="login.form.email_placeholder"/>
          </div>
```

Note the `<label>` text had to be wrapped in a `<span data-i18n="...">` since the label mixes a literal icon element with a text node — `data-i18n` only ever replaces `el.textContent` wholesale, so it must target an element that contains *only* the translatable text, not siblings like the icon `<span>`.

Add to `DICT` in `i18n.js`:
```js
// en
"login.brand.title": "Access Gate",
"login.brand.subtitle": "Sovereign Intelligence Protocol",
"login.form.title": "Secure Identity Verification",
"login.form.subtitle": "Authorized personnel only.",
"login.form.email_label": "Institutional Email",
"login.form.email_placeholder": "name@sydeco.legal",
// id
"login.brand.title": "Gerbang Akses",
"login.brand.subtitle": "Protokol Intelijen Berdaulat",
"login.form.title": "Verifikasi Identitas Aman",
"login.form.subtitle": "Khusus personel yang berwenang.",
"login.form.email_label": "Email Institusi",
"login.form.email_placeholder": "nama@sydeco.legal",
```

- [ ] **Step 4: Tag the rest of `login.html`'s static chrome**

Walk the remaining auth states (password field, submit button, MFA challenge screen, MFA enrollment screen, recovery-code screen, error messages that are static copy rather than server-returned text) and tag every literal string with `login.<section>.<element>` keys, following the same `data-i18n` / `data-i18n-placeholder` / wrapping-span pattern from Step 3. Server-returned error messages (anything bound via `x-text` to a variable populated from a fetch response) stay untouched.

- [ ] **Step 5: Verify dictionary parity**

Run: `node ldv-frontend/i18n.selfcheck.js`
Expected: `OK: N keys, EN/ID parity confirmed.`

- [ ] **Step 6: Manual browser verification**

With the Flask dev server running, open `/login`, toggle the language pill, confirm all screens (login form, and — using a test account — the MFA challenge/enrollment screens) switch language correctly and the button state (`EN`/`ID`) tracks correctly across the multi-step form without a reload.

- [ ] **Step 7: Commit**

```bash
git add ldv-frontend/login.html ldv-frontend/i18n.js
git commit -m "feat: add EN/ID language toggle to login.html"
```

---

### Task 5: Wire the toggle into `account.html`, translate its chrome, and establish the Alpine `x-text` translation pattern

**Files:**
- Modify: `ldv-frontend/account.html` (head scripts, `:254` body open, `:263-282` header + MFA status section, plus the rest of the page)

**Interfaces:**
- Consumes: `window.i18n` (including `i18n.t()` and `Alpine.store('lang')`) from Task 1.
- Produces: `account.*` keys, and the reference implementation of the "Alpine `x-text` + `i18n.t()` + `$store.lang`" pattern that Task 2/3/6/7 fall back to whenever they hit a dynamic-but-app-internal string (not literal text, not API content).

- [ ] **Step 1: Load `i18n.js` in `<head>`** — same pattern as Task 2 Step 1.

- [ ] **Step 2: Add the toggle button right after `<body ...>` (line 254)** — identical snippet to Task 2 Step 2.

- [ ] **Step 3: Tag the static header (worked example) — lines 256-266**

Before:
```html
    <a href="/" class="flex items-center gap-2 text-sm font-bold font-body text-on-surface-variant hover:text-primary transition-colors" style="text-decoration:none;">
      <span class="material-symbols-outlined text-[18px]">arrow_back</span>
      Back to Sydeco CRA
    </a>
    <a href="/logout" class="text-xs font-semibold text-on-surface-variant hover:text-primary transition-colors" style="text-decoration:none;">Secure Logout</a>
  </header>

  <main class="pt-28 pb-20 px-6 max-w-2xl mx-auto">
    <h1 class="font-editorial text-3xl mb-2">Account & Security</h1>
```

After:
```html
    <a href="/" class="flex items-center gap-2 text-sm font-bold font-body text-on-surface-variant hover:text-primary transition-colors" style="text-decoration:none;">
      <span class="material-symbols-outlined text-[18px]">arrow_back</span>
      <span data-i18n="account.header.back_link">Back to Sydeco CRA</span>
    </a>
    <a href="/logout" class="text-xs font-semibold text-on-surface-variant hover:text-primary transition-colors" style="text-decoration:none;" data-i18n="nav.secure_logout">Secure Logout</a>
  </header>

  <main class="pt-28 pb-20 px-6 max-w-2xl mx-auto">
    <h1 class="font-editorial text-3xl mb-2" data-i18n="account.header.title">Account & Security</h1>
```

- [ ] **Step 4: Translate the Alpine-bound MFA status text (worked example — the dynamic-string pattern) — lines 271-282**

This section's text is generated by inline Alpine ternaries, not literal DOM text, so `data-i18n` (which only ever runs once per `applyLang()` DOM pass) cannot target it — Alpine re-runs these expressions on its own whenever `mfaEnabled`/`mfaMandatory` change, and would stomp any one-time translation. Instead, route the expression itself through `i18n.t()`, and force Alpine to re-evaluate on language change by referencing `$store.lang`.

Before:
```html
      <div>
        <h2 class="font-editorial text-lg font-bold text-primary">Multi-Factor Authentication</h2>
        <p class="text-xs text-on-surface-variant mt-1" x-text="mfaMandatory ? 'Mandatory for your organization or role.' : 'Optional — recommended for institutional accounts.'"></p>
      </div>
      <span class="px-3 py-1 rounded text-xs font-bold uppercase tracking-wider border"
            :class="mfaEnabled ? 'bg-teal-950/40 text-teal-400 border-teal-500/20' : 'bg-amber-950/40 text-amber-300 border-amber-500/20'"
            x-text="mfaEnabled ? 'Enabled' : 'Disabled'"></span>
    </div>

    <button type="button" class="gold-button px-6 py-2.5 rounded text-xs font-bold uppercase tracking-wider"
            x-show="!mfaEnabled" @click="view = 'enable_password'">Enable MFA</button>

    <button type="button" class="px-6 py-2.5 rounded text-xs font-bold uppercase tracking-wider border border-red-500/30 text-red-400 hover:bg-red-950/20 transition-colors"
            x-show="mfaEnabled" @click="view = 'disable_password'">Disable MFA</button>
```

After:
```html
      <div>
        <h2 class="font-editorial text-lg font-bold text-primary" data-i18n="account.mfa.title">Multi-Factor Authentication</h2>
        <p class="text-xs text-on-surface-variant mt-1" x-text="$store.lang && (mfaMandatory ? i18n.t('account.mfa.mandatory_note') : i18n.t('account.mfa.optional_note'))"></p>
      </div>
      <span class="px-3 py-1 rounded text-xs font-bold uppercase tracking-wider border"
            :class="mfaEnabled ? 'bg-teal-950/40 text-teal-400 border-teal-500/20' : 'bg-amber-950/40 text-amber-300 border-amber-500/20'"
            x-text="$store.lang && (mfaEnabled ? i18n.t('account.mfa.enabled') : i18n.t('account.mfa.disabled'))"></span>
    </div>

    <button type="button" class="gold-button px-6 py-2.5 rounded text-xs font-bold uppercase tracking-wider"
            x-show="!mfaEnabled" @click="view = 'enable_password'" data-i18n="account.mfa.enable_button">Enable MFA</button>

    <button type="button" class="px-6 py-2.5 rounded text-xs font-bold uppercase tracking-wider border border-red-500/30 text-red-400 hover:bg-red-950/20 transition-colors"
            x-show="mfaEnabled" @click="view = 'disable_password'" data-i18n="account.mfa.disable_button">Disable MFA</button>
```

(`$store.lang &&` is a no-op on the boolean result — `$store.lang` is always a truthy `"en"`/`"id"` string — its only purpose is to give Alpine's dependency tracker a reason to re-run the expression when `Alpine.store('lang', ...)` changes inside `applyLang()`.)

Add to `DICT` in `i18n.js`:
```js
// en
"account.header.back_link": "Back to Sydeco CRA",
"account.header.title": "Account & Security",
"account.mfa.title": "Multi-Factor Authentication",
"account.mfa.mandatory_note": "Mandatory for your organization or role.",
"account.mfa.optional_note": "Optional — recommended for institutional accounts.",
"account.mfa.enabled": "Enabled",
"account.mfa.disabled": "Disabled",
"account.mfa.enable_button": "Enable MFA",
"account.mfa.disable_button": "Disable MFA",
// id
"account.header.back_link": "Kembali ke Sydeco CRA",
"account.header.title": "Akun & Keamanan",
"account.mfa.title": "Autentikasi Multi-Faktor",
"account.mfa.mandatory_note": "Wajib untuk organisasi atau peran Anda.",
"account.mfa.optional_note": "Opsional — direkomendasikan untuk akun institusi.",
"account.mfa.enabled": "Aktif",
"account.mfa.disabled": "Nonaktif",
"account.mfa.enable_button": "Aktifkan MFA",
"account.mfa.disable_button": "Nonaktifkan MFA",
```

- [ ] **Step 5: Tag the rest of `account.html`'s static chrome**

Walk the remaining sections (org/download-access settings if present, form labels, buttons, success/error banners that are static copy). Use `data-i18n` for literal text; use the `i18n.t()` + `$store.lang` pattern from Step 4 for any other Alpine `x-text` expression that isn't purely rendering API/user data.

- [ ] **Step 6: Verify dictionary parity**

Run: `node ldv-frontend/i18n.selfcheck.js`
Expected: `OK: N keys, EN/ID parity confirmed.`

- [ ] **Step 7: Manual browser verification**

Log in, go to `/account`, toggle language. Confirm the MFA status text (mandatory/optional, enabled/disabled) updates immediately alongside the static labels — this is the key check that the `$store.lang` reactivity trick actually works, not just the plain `data-i18n` pass.

- [ ] **Step 8: Commit**

```bash
git add ldv-frontend/account.html ldv-frontend/i18n.js
git commit -m "feat: add EN/ID language toggle to account.html"
```

---

### Task 6: Wire the toggle into `admin.html`, translate its chrome, and define the shared sidebar keys

**Files:**
- Modify: `ldv-frontend/admin.html` (head scripts, `:258` body open, `:261-270` top header, `:292-343` sidebar nav, `:1179-1183` `getTabTitle()` JS function, plus the rest of the dashboard tabs)

**Interfaces:**
- Consumes: `window.i18n` from Task 1, the `i18n.t()` + `$store.lang` pattern from Task 5.
- Produces: `nav.sidebar.*` keys — **Task 7 (`citations.html`) reuses these verbatim** since its sidebar markup is byte-for-byte identical. Do not redefine them in Task 7.

- [ ] **Step 1: Load `i18n.js` in `<head>`** — same pattern as Task 2 Step 1.

- [ ] **Step 2: Add the toggle button right after `<body ...>` (line 258)** — identical snippet to Task 2 Step 2.

- [ ] **Step 3: Tag the top header breadcrumb (worked example) — lines 265-269**

Before:
```html
      <a href="/admin" class="hover:text-primary transition-colors text-on-surface-variant/80 hidden sm:inline shrink-0" style="text-decoration:none;">Admin Portal</a>
      <span class="material-symbols-outlined text-[16px] text-on-surface-variant/30 hidden sm:inline shrink-0">chevron_right</span>
      <span class="text-primary font-bold truncate" x-text="getTabTitle()">System Administration</span>
    </div>
    <a href="/" class="text-sm font-bold font-body uppercase tracking-wider px-3 sm:px-5 py-2 rounded bg-primary text-on-primary hover:brightness-110 transition-all shadow-md shadow-primary/10 whitespace-nowrap shrink-0" style="text-decoration:none;">+ New<span class="hidden sm:inline"> Analysis</span></a>
```

After (the `getTabTitle()` fix is Step 4 below — this element itself doesn't change beyond the breadcrumb label and the "+ New Analysis" button, since `x-text="getTabTitle()"` already re-runs reactively and Step 4 makes `getTabTitle()` itself language-aware):
```html
      <a href="/admin" class="hover:text-primary transition-colors text-on-surface-variant/80 hidden sm:inline shrink-0" style="text-decoration:none;" data-i18n="nav.sidebar.admin_portal">Admin Portal</a>
      <span class="material-symbols-outlined text-[16px] text-on-surface-variant/30 hidden sm:inline shrink-0">chevron_right</span>
      <span class="text-primary font-bold truncate" x-text="getTabTitle()">System Administration</span>
    </div>
    <a href="/" class="text-sm font-bold font-body uppercase tracking-wider px-3 sm:px-5 py-2 rounded bg-primary text-on-primary hover:brightness-110 transition-all shadow-md shadow-primary/10 whitespace-nowrap shrink-0" style="text-decoration:none;"><span data-i18n="admin.header.new_analysis_prefix">+ New</span><span class="hidden sm:inline" data-i18n="admin.header.new_analysis_suffix"> Analysis</span></a>
```

- [ ] **Step 4: Make `getTabTitle()` language-aware — around line 1179**

Find the `getTabTitle()` implementation (near the `team: 'Team Management'` / `orgs: 'Organizations'` / `status: 'System Health Status'` map at line ~1179). Replace the hardcoded English map with `i18n.t()` lookups:

Before:
```js
            team: 'Team Management',
            orgs: 'Organizations',
```
*(and its sibling entries for `overview`, `audits`, `status`, in the same object)*

After:
```js
            team: i18n.t('nav.sidebar.team_management'),
            orgs: i18n.t('nav.sidebar.organizations'),
```
*(apply the same `i18n.t('nav.sidebar.<key>')` substitution to every entry in that title map — `overview`, `audits`, `status` — using the key names from Step 5's sidebar tagging so the breadcrumb and the sidebar link always say the same thing in the same language)*

Since `getTabTitle()` is called from `x-text="getTabTitle()"`, which Alpine only re-runs when `activeTab` (a reactive property it already reads) changes — not when only the language flips — also change the binding to force a re-check on language change, matching the Task 5 pattern:

```html
<span class="text-primary font-bold truncate" x-text="$store.lang && getTabTitle()">System Administration</span>
```

- [ ] **Step 5: Tag the sidebar nav (worked example) — lines 292-343**

Before:
```html
      <!-- Core Operations -->
      <div class="px-6 mb-2 mt-4 text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/40">Core Operations</div>
      <a class="flex items-center gap-3 px-4 py-3 mx-2 text-on-surface-variant hover:bg-surface-variant/30 hover:text-primary rounded-lg transition-all" href="/">
        <span class="material-symbols-outlined">upload_file</span>
        <span class="text-sm font-semibold">New Analysis</span>
      </a>
```
*(and the equivalent unmodified markup for the Overview / Management / Team Management / Organizations / Compliance & Health / Audit Logs / System Health / Secure Logout entries already shown in the design exploration)*

After (pattern applied to every sidebar link):
```html
      <!-- Core Operations -->
      <div class="px-6 mb-2 mt-4 text-[10px] font-bold uppercase tracking-widest text-on-surface-variant/40" data-i18n="nav.sidebar.core_operations">Core Operations</div>
      <a class="flex items-center gap-3 px-4 py-3 mx-2 text-on-surface-variant hover:bg-surface-variant/30 hover:text-primary rounded-lg transition-all" href="/">
        <span class="material-symbols-outlined">upload_file</span>
        <span class="text-sm font-semibold" data-i18n="nav.new_analysis">New Analysis</span>
      </a>
```

Apply the same `data-i18n` treatment to every remaining sidebar entry, using these exact keys (so Task 7 can reuse them unchanged): `nav.sidebar.core_operations`, `nav.sidebar.overview` (label "Overview"), `nav.sidebar.management` (section header "Management"), `nav.sidebar.team_management`, `nav.sidebar.organizations`, `nav.sidebar.compliance_health` (section header "Compliance & Health"), `nav.sidebar.citation_library` (reuse the existing `nav.citation_library` key instead — same string, same key, already seeded in Task 1), `nav.sidebar.audit_logs`, `nav.sidebar.system_health`, and `nav.sidebar.admin_portal` (from Step 3). `nav.secure_logout` (already seeded) covers the sidebar's logout link too.

Add to `DICT` in `i18n.js`:
```js
// en
"nav.sidebar.admin_portal": "Admin Portal",
"nav.sidebar.core_operations": "Core Operations",
"nav.sidebar.overview": "Overview",
"nav.sidebar.management": "Management",
"nav.sidebar.team_management": "Team Management",
"nav.sidebar.organizations": "Organizations",
"nav.sidebar.compliance_health": "Compliance & Health",
"nav.sidebar.audit_logs": "Audit Logs",
"nav.sidebar.system_health": "System Health",
"admin.header.new_analysis_prefix": "+ New",
"admin.header.new_analysis_suffix": " Analysis",
// id
"nav.sidebar.admin_portal": "Portal Admin",
"nav.sidebar.core_operations": "Operasi Inti",
"nav.sidebar.overview": "Ikhtisar",
"nav.sidebar.management": "Manajemen",
"nav.sidebar.team_management": "Manajemen Tim",
"nav.sidebar.organizations": "Organisasi",
"nav.sidebar.compliance_health": "Kepatuhan & Kesehatan",
"nav.sidebar.audit_logs": "Log Audit",
"nav.sidebar.system_health": "Kesehatan Sistem",
"admin.header.new_analysis_prefix": "+ Baru",
"admin.header.new_analysis_suffix": " Analisis",
```

- [ ] **Step 6: Tag the rest of `admin.html`'s static chrome**

Walk the remaining dashboard tabs (System Overview, Team Management, Organizations, Audit Logs, System Health panels — headings, table column headers, buttons, modal labels, empty-states). Tag literal text with `admin.<section>.<element>` keys; use the `i18n.t()` + `$store.lang` pattern (Task 5 Step 4) for any other dynamic Alpine-bound label. Leave all data pulled from `/api/v1/admin/*` endpoints (user emails, org names, audit log entries, stats numbers) untouched.

- [ ] **Step 7: Verify dictionary parity**

Run: `node ldv-frontend/i18n.selfcheck.js`
Expected: `OK: N keys, EN/ID parity confirmed.`

- [ ] **Step 8: Manual browser verification**

Log in as an admin, open `/admin`, toggle language. Confirm the sidebar, top breadcrumb (including the `getTabTitle()`-driven label), and each tab's static chrome switch correctly, and that clicking between tabs still shows the correctly-translated title in whichever language is currently active.

- [ ] **Step 9: Commit**

```bash
git add ldv-frontend/admin.html ldv-frontend/i18n.js
git commit -m "feat: add EN/ID language toggle to admin.html"
```

---

### Task 7: Wire the toggle into `citations.html` and translate its chrome (reusing admin's sidebar keys)

**Files:**
- Modify: `ldv-frontend/citations.html` (head scripts, `:236` body open, `:239-248` top header, `:268-311` sidebar nav — identical to `admin.html`'s, `:321-325` page header, plus the rest of the citation review UI)

**Interfaces:**
- Consumes: `window.i18n` from Task 1, and the `nav.sidebar.*` keys **already defined by Task 6** — this task must not redefine them.

- [ ] **Step 1: Load `i18n.js` in `<head>`** — same pattern as Task 2 Step 1.

- [ ] **Step 2: Add the toggle button right after `<body ...>` (line 236)** — identical snippet to Task 2 Step 2.

- [ ] **Step 3: Tag the top header and sidebar (worked example, reusing Task 6's keys) — lines 239-248 and 268-311**

Before:
```html
      <a href="/admin" class="hover:text-primary transition-colors text-on-surface-variant/80 hidden sm:inline shrink-0" style="text-decoration:none;">Admin Portal</a>
      <span class="material-symbols-outlined text-[16px] text-on-surface-variant/30 hidden sm:inline shrink-0">chevron_right</span>
      <span class="text-primary font-bold truncate">Citation Library</span>
```

After:
```html
      <a href="/admin" class="hover:text-primary transition-colors text-on-surface-variant/80 hidden sm:inline shrink-0" style="text-decoration:none;" data-i18n="nav.sidebar.admin_portal">Admin Portal</a>
      <span class="material-symbols-outlined text-[16px] text-on-surface-variant/30 hidden sm:inline shrink-0">chevron_right</span>
      <span class="text-primary font-bold truncate" data-i18n="nav.citation_library">Citation Library</span>
```

For the sidebar (lines 268-311), apply `data-i18n="nav.sidebar.core_operations"`, `data-i18n="nav.new_analysis"`, `data-i18n="nav.sidebar.overview"`, `data-i18n="nav.sidebar.management"`, `data-i18n="nav.sidebar.team_management"`, `data-i18n="nav.sidebar.organizations"`, `data-i18n="nav.sidebar.compliance_health"`, `data-i18n="nav.citation_library"`, `data-i18n="nav.sidebar.audit_logs"`, `data-i18n="nav.sidebar.system_health"`, `data-i18n="nav.secure_logout"` to the matching elements — same keys Task 6 already put into `DICT`, so **no new dictionary entries are added in this step**.

- [ ] **Step 4: Tag the page header (worked example) — lines 321-325**

Before:
```html
      <header class="mb-12">
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div>
            <h1 class="font-editorial text-headline-lg md:text-display-lg text-on-surface mb-2">Legal Authority <span class="gold-gradient-text">Verification</span></h1>
            <p class="font-body text-body-lg text-on-surface-variant max-w-2xl">A secure protocol for reviewing, verifying, and versioning legal citations within the sovereign intelligence architecture.</p>
```

After:
```html
      <header class="mb-12">
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div>
            <h1 class="font-editorial text-headline-lg md:text-display-lg text-on-surface mb-2"><span data-i18n="citations.header.title_prefix">Legal Authority</span> <span class="gold-gradient-text" data-i18n="citations.header.title_suffix">Verification</span></h1>
            <p class="font-body text-body-lg text-on-surface-variant max-w-2xl" data-i18n="citations.header.subtitle">A secure protocol for reviewing, verifying, and versioning legal citations within the sovereign intelligence architecture.</p>
```

Add to `DICT` in `i18n.js`:
```js
// en
"citations.header.title_prefix": "Legal Authority",
"citations.header.title_suffix": "Verification",
"citations.header.subtitle": "A secure protocol for reviewing, verifying, and versioning legal citations within the sovereign intelligence architecture.",
// id
"citations.header.title_prefix": "Otoritas Hukum",
"citations.header.title_suffix": "Verifikasi",
"citations.header.subtitle": "Protokol aman untuk meninjau, memverifikasi, dan mengelola versi sitasi hukum dalam arsitektur intelijen berdaulat.",
```

- [ ] **Step 5: Tag the rest of `citations.html`'s static chrome**

Walk the citation review table/list UI (column headers, filter labels, verify/reject buttons, status badges, empty-states). Tag literal text with `citations.<section>.<element>` keys; use the `i18n.t()` + `$store.lang` pattern for dynamic Alpine-bound labels. Leave all citation data pulled from `/api/v1/citations` (citation text, clause names, jurisdictions, verification status values that come from the CSV) untouched.

- [ ] **Step 6: Verify dictionary parity**

Run: `node ldv-frontend/i18n.selfcheck.js`
Expected: `OK: N keys, EN/ID parity confirmed.`

- [ ] **Step 7: Manual browser verification**

Log in as admin/reviewer, open `/citations`, toggle language. Confirm the sidebar/breadcrumb match `admin.html`'s translations exactly (proving key reuse worked), and the page-specific chrome (title, subtitle, table headers, buttons) translates correctly while citation data itself stays as returned by the API.

- [ ] **Step 8: Commit**

```bash
git add ldv-frontend/citations.html ldv-frontend/i18n.js
git commit -m "feat: add EN/ID language toggle to citations.html"
```

---

## Final check (after all 7 tasks)

- [ ] Run `node ldv-frontend/i18n.selfcheck.js` one last time from a clean checkout — expect full EN/ID parity across every key accumulated from all 6 pages.
- [ ] Grep for any page missing the toggle: `grep -L "data-lang-toggle" ldv-frontend/*.html` — expect no output (every page has it) except `swagger.html` (API docs page, intentionally out of scope — it's developer tooling, not end-user UI).
- [ ] Click through all 6 pages in the browser with the toggle set to `ID`, then back to `EN`, confirming no page shows a mix of leftover English chrome next to translated chrome.
