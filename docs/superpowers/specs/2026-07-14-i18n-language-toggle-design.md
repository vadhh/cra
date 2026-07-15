# Indonesian/English Language Toggle for the Frontend

Date: 2026-07-14

## Context

The Sydeco CRA frontend (`ldv-frontend/`) is six static HTML pages
(`index.html`, `result.html`, `login.html`, `account.html`, `admin.html`,
`citations.html`) served as-is by `app.py` via `send_from_directory` — no
templating engine, no build step. Every page loads Tailwind (CDN) and
Alpine.js (CDN) directly and hardcodes its UI text in English.

The backend already resolves clause guidance (Reason/Recommendation/
Business_Impact via `clause_db.clause_guidance()`) in the *document's own*
detected language (EN/ID/FR), independent of any UI setting — see
`_run_analysis(..., lang=...)` in `app.py`. That mechanism is unrelated to
this feature and is not touched.

**Goal:** add a language toggle button, present on all six pages, that
switches the app's static UI chrome (nav, buttons, headings, labels,
empty-states, table headers, tooltips) between English and Indonesian.
Content sourced from the API at runtime (analysis results, red flags,
clause guidance, user/org data) is explicitly out of scope and continues
to render in whatever language the backend already returns.

## Architecture

Pure client-side, vanilla JS, no new dependencies.

### `ldv-frontend/i18n.js` (new, shared across all 6 pages)

- `const DICT = { en: { key: "...", ... }, id: { key: "...", ... } }` — one
  flat key → string map per language.
- `getLang()` — reads `localStorage.getItem("ldv_lang")`, defaults to
  `"en"` if unset or not one of `"en"`/`"id"`.
- `setLang(lang)` — writes `localStorage.setItem("ldv_lang", lang)`, then
  calls `applyLang()`.
- `applyLang()`:
  - `document.documentElement.lang = getLang()`
  - For every `el` in `document.querySelectorAll("[data-i18n]")`: look up
    `DICT[getLang()][el.dataset.i18n]`. If found, set `el.textContent` to
    it. If not found (missing translation), leave the element's existing
    text untouched — the literal English text already sitting in the HTML
    is the fallback, so a missing key never blanks the UI.
  - Same pass for `[data-i18n-placeholder]` against the `placeholder`
    attribute (for inputs whose placeholder text needs translation).
  - Updates the toggle button's own pressed/active state.
- Runs `applyLang()` once on `DOMContentLoaded`.

No Alpine store, no reactivity framework tie-in — plain DOM text swap.
Keeps it usable identically across all 6 pages regardless of whether that
page happens to use Alpine for other things.

### Toggle button

A single small reusable snippet (`EN | ID` two-state pill, gold/obsidian
themed to match the existing design tokens) added once per page, near the
top-of-page branding/header. Since there's no include mechanism, the same
~10 lines of markup are pasted into each of the 6 pages (mechanical,
low-risk). Click handler calls `i18n.setLang(otherLang)`.

Placement: fixed-position top-right corner on every page. Chosen over
threading it into each page's differently-shaped header (some pages have
a persistent top navbar, `login.html` has none — just a centered card) so
one consistent component works everywhere without bespoke layout work per
page.

### String tagging

Every static UI string across the 6 pages gets wrapped or annotated with
`data-i18n="some.key"` (dot-namespaced per page/section, e.g.
`index.hero.title`, `login.form.email_label`). Existing English text stays
as the element's literal content (doubles as the fallback). Inputs needing
translated placeholders get `data-i18n-placeholder="some.key"` instead.

Out of scope for tagging: anything rendered from API responses at
runtime (`x-text`/`innerHTML` bound to JS variables holding
analysis/user/org data).

## Data flow

1. Page loads → `i18n.js` runs → `applyLang()` reads `localStorage`
   (default `en`) → swaps all tagged elements to that language.
2. User clicks the toggle → `setLang()` flips the stored language and
   re-runs `applyLang()` → whole page updates instantly, no reload,
   no network request.
3. Choice persists via `localStorage` across pages and future visits
   (shared across all 6 pages since they're same-origin).

## Error handling / fallback

- Missing translation key → falls back to the English text already in
  the DOM (never renders blank or `undefined`).
- Unrecognized `localStorage` value (corrupted/old) → `getLang()`
  defaults to `"en"`.
- No dependency on the network or any backend endpoint — this is 100%
  client-side, so it can't fail from an API outage.

## Testing

Non-trivial logic here is the lookup/fallback behavior in `applyLang()`
and dictionary completeness. Per project convention, one small runnable
check: `ldv-frontend/i18n.selfcheck.js` (plain Node script, no test
framework) that:

1. Loads `DICT` from `i18n.js`.
2. Asserts `Object.keys(DICT.en)` and `Object.keys(DICT.id)` are identical
   sets — catches a key present in English with no Indonesian
   translation (or vice versa) before it ships.
3. Exits non-zero with the missing/extra keys listed if the assertion
   fails.

Run manually (`node ldv-frontend/i18n.selfcheck.js`) after adding new
strings; not wired into CI since this project has no JS test runner
today.

## Effort note

This touches all 6 pages and tags every static string in them — a real,
mechanical chunk of work (expect on the order of a few hundred
`data-i18n` keys total across the app, each needing an Indonesian
translation). The implementation plan should sequence this
page-by-page rather than attempt it as one diff.
