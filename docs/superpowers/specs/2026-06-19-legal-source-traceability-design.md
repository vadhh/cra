# Legal Source Traceability — Design

**Date:** 2026-06-19
**Status:** Approved design, pre-implementation
**Roadmap:** R1 — Detection upgrades; TODO P2 #7

## Problem

Lawyers won't trust the analyzer's flagged risks without article citations
(e.g. "Article 1844-1, French Code civil" next to a leonine clause). The
codebase has **zero** citation functionality today and no citation data
anywhere. We build the source of truth from scratch.

## Hard constraint

Citations must be **deterministic and lawyer-verifiable**. They are never
LLM-generated — a hallucinated "Article 1794" is worse than no citation in a
legal tool. The citation table is lawyer-authored *data*; code only looks it
up. Claude seeds confidently-known citations but marks them `draft` until a
lawyer verifies them.

## Scope

All findings carry citations: red flags **and** clauses (both detected and
missing). One mechanism annotates every finding by its stable `id`.

## Architecture

Three units, each independently testable:

### 1. Data — `datasets/legal_citations.csv`

Lawyer-authored, mirrors `datasets/required_clauses.csv`. Schema:

```
finding_id, jurisdiction, article, source, note, status
```

- `finding_id` — existing stable IDs from `_RED_FLAGS` (`leonine_no_loss`,
  `excessive_penalty`, `rights_waiver`, …) and `_CLAUSE_RULES`
  (`governing_law`, `termination`, …). One namespace; IDs are already distinct.
- `jurisdiction` — detector codes: `BE / FR / ID / NL / EN&W / US / generic`.
  `generic` is the fallback row used when no jurisdiction-specific row exists.
- `article` — the citation string (may be empty for a generic explanatory note).
- `source` — the code/statute name.
- `note` — short plain-language rationale.
- `status` — `verified | draft`. **The trust boundary.** Claude's seeds are
  `draft`; a lawyer reviews and flips to `verified`. Returned to the client so
  the frontend can badge unverified citations rather than the API hiding them.

Ships with a confident seed (clearest red-flag→article mappings, marked
`draft`); grows under legal review. No requirement to fill all id×jurisdiction
cells.

### 2. Adapter — `detector/citation_db.py`

Near-clone of `detector/clause_db.py`. Lazy CSV singleton, fail-soft (missing
or malformed CSV disables citations, never breaks analysis).

Public API:

- `citations_for(finding_id, jurisdiction) -> list[dict]` — rows for the given
  finding, preferring the detected jurisdiction, falling back to `generic`.
  Returns `[]` when nothing matches (never raises). Each dict:
  `{article, source, note, status, jurisdiction}`.
- `annotate_layer1(layer1, jurisdiction) -> layer1` — attaches a
  `citations: [...]` array onto each `red_flags[]` entry and each
  `clause_presence[]` entry, keyed by the entry's `id`. Pure enrichment;
  mutates/returns the layer1 dict, empty array when no citation exists.
- `verify_against(valid_ids) -> list[str]` — drift guard. Returns CSV
  `finding_id`s that are no longer real rule/clause IDs (same pattern as
  `clause_db.verify_mappings()`).
- `db_available() -> bool`.

Jurisdiction normalization (Belgium→BE, France→FR, Indonesia→ID,
Netherlands→NL, …) lives in this module; unknown names → `generic`.

### 3. Wiring — `app.py`

After L1 runs, `app.py` calls
`citation_db.annotate_layer1(layer1, detected_jurisdiction)` before assembling
the response. `detector_rules.py` is untouched — detection stays pure, legal
data never couples to detection logic.

## Data flow

```
text → layer1_analyze() → layer1 {red_flags[], clause_presence[], …}
     → citation_db.annotate_layer1(layer1, jurisdiction)
         → each red_flags[i].citations  = citations_for(id, juris)
         → each clause_presence[i].citations = citations_for(id, juris)
     → response JSON (citations inline on each finding)
```

## Error handling

- CSV missing/malformed → `db_available()` false, `citations_for` returns `[]`,
  analysis proceeds uncited. Logged once, like `clause_db`.
- Unknown/undetected jurisdiction → `generic` rows, else `[]`.
- A finding with no matching row → empty `citations` array (uniform client
  contract: the key is always present).

## Testing

`python3 detector/citation_db.py` self-check:
1. CSV loads and `db_available()` is true.
2. `verify_against(<real ids>)` is empty (no drift — every cited `finding_id`
   is a live rule/clause ID).
3. A known seed lookup returns the expected citation
   (e.g. `citations_for("leonine_no_loss", "FR")` is non-empty and `draft`).

Mirrors the `clause_db.py` `__main__` self-check. No framework.

## Decisions (settled, not open)

- Citations default-on — deterministic dict lookup, negligible cost.
- `status` field surfaced to client; API does not silently hide `draft`
  citations — honesty over concealment, frontend badges them.
- Inline on each finding (no separate top-level block, no client-side join).

## Out of scope (YAGNI)

- No per-jurisdiction generated prose.
- No L4 / Qwen involvement (would re-introduce hallucination risk).
- No external legal API (sovereignty + latency).
- No exhaustive id×jurisdiction authoring — seed + legal review.
- No env toggle — citations are free and always useful.

## Note

Repo is not a git repository (`git init` not run), so this spec is written but
not committed. Commit when version control is established.
