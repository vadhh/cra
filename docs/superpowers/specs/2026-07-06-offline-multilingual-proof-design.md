# P0 Priority 1 — Offline Multilingual Proof Design Spec

**Date:** 2026-07-06
**Maps to:** External review acceptance requirements (2026-07-06 management directive), CLAUDE.md P1 #11 (local translation), TODO P0 acceptance gate.
**Status:** proposed design.

## Problem

The 2026-06-22 external review and the 2026-07-06 management directive both require proof — not a claim — that LDV can analyze contracts in English, Indonesian, French, and Dutch **without any network access and without transmitting contract text externally**. Local Marian MT translation (`LDV_REMOTE_TRANSLATION=local`) was implemented and marked DONE in CLAUDE.md, but:

- It has never been run with the network actually blocked.
- One of the three required language models (`Helsinki-NLP/opus-mt-fr-en`) is not yet downloaded into the local cache.
- No test fixtures exist for non-contract documents in FR/NL/ID (only English non-contract fixtures exist).
- No report has broken results down per-language with the specific metrics management asked for (doc-type accuracy, clause recall, red-flag precision/recall, evidence-span correctness, timing percentiles, peak RAM, translation failures, model versions).
- Prior reports were Markdown pasted into Word and used local `/home/stardhoom/...` file links — unusable by anyone outside this machine. This report must not repeat that mistake.

"The workspace is clean" / "the suite was created" is explicitly rejected as evidence. This spec produces a runnable, repeatable offline test harness and a self-contained PDF report with concrete pass/fail numbers.

## Decisions

1. **Enforce offline via a socket-level trap, not physical disconnection.** This is a dev sandbox, not the real deployment target — there's no safe way to sever the box's actual network without affecting the rest of the session/toolchain. Instead, `tests/run_offline_validation.py` monkeypatches `socket.socket.connect` (and `socket.create_connection`) for the duration of the run to raise `RuntimeError` on any non-loopback address. This proves the analysis code path makes zero outbound calls, which is the actual property being certified. `ponytail: this covers the interpreter's socket layer, not raw syscalls — sufficient to prove this codebase makes no outbound calls under test, not a full network-namespace sandbox. Upgrade to a network-namespace/iptables block only if a future audit needs kernel-level proof.`
2. **Force local translation, not "no translation."** `LDV_REMOTE_TRANSLATION=local` is set for the run (not the default `0`, which skips translation entirely and would make FR/NL/ID documents untranslated going into L2/L4). This is what actually exercises the offline Marian MT path the review is asking about.
3. **Reuse `run_benchmark.py`'s fixture/expectation pattern instead of a parallel framework.** New per-language metrics collection wraps the existing `_run_analysis` call already used there; no new test framework.
4. **Reuse `pdf_report.py` / `reportlab` for the deliverable**, not `python-docx` (per user correction — output is PDF) and not hand-formatted Markdown. `reportlab==4.5.1` is already a pinned dependency.
5. **New fixtures only where a real gap exists**: FR/NL/ID non-contract documents. Existing EN non-contract, and EN/FR/NL/ID contract fixtures are reused as-is. One scanned/malformed case is already covered by the existing `negative/` fixtures plus the existing `ValueError("Scan/OCR required...")` fail-closed path in `app.py:197` — no OCR needs to be built, the test just asserts that path is hit and reported, not silently swallowed.

## Architecture

### 1. Model cache completion
One-time, online step (documented as such in the report, not hidden): download `Helsinki-NLP/opus-mt-fr-en` into `~/.cache/huggingface/hub/` alongside the already-cached `opus-mt-id-en` and `opus-mt-nl-en`. This happens *before* the offline run and is explicitly logged as a setup step, not part of the "offline" claim.

### 2. New fixtures (`tests/create_fixtures.py` additions)
Three new files following the existing generator pattern:
- `docx/06_memo_fr.docx` — French internal legal memo (non-contract)
- `docx/07_brochure_nl.docx` — Dutch marketing brochure (non-contract)
- `txt/16_notice_id.txt` — Indonesian public notice (non-contract)

Each gets an `expected: {"is_contract": False, "language": "fr"|"nl"|"id"}` entry in the benchmark suite.

### 3. Offline harness (`tests/run_offline_validation.py`, new)
```python
# ponytail: socket trap proves "no outbound calls", not kernel-level isolation
import socket
_orig_connect = socket.socket.connect

def _blocked_connect(self, address):
    host = address[0] if isinstance(address, tuple) else address
    if host not in ("127.0.0.1", "::1", "localhost"):
        raise RuntimeError(f"BLOCKED offline-mode outbound connect to {address}")
    return _orig_connect(self, address)
```
Applied via `socket.socket.connect = _blocked_connect` for the duration of the run, restored in a `finally` block. A `self_check()` runs first: attempt a deliberate outbound connect and assert it raises, proving the trap is live before trusting the "0 external calls" claim in the report.

Sets `os.environ["LDV_REMOTE_TRANSLATION"] = "local"` for the run, then imports and drives the pipeline exactly like `run_benchmark.py` does (`_run_analysis`, `_extract_pdf/_extract_docx/_extract_txt`).

### 4. Per-language metrics collection
For each fixture, capture:
- language (detected vs. expected)
- document_type correctness (predicted vs. expected, from L2)
- required-clause recall (present/expected present, from L3 `required_clauses`)
- red-flag precision/recall (found vs. expected, from L1+L2 red flags)
- evidence-span correctness (existing evidence-span field vs. expected substring presence)
- wall-clock latency (`time.perf_counter()` around `_run_analysis`)
- peak RSS (`resource.getrusage(resource.RUSAGE_SELF).ru_maxrss`, sampled after each fixture, reported as a running peak — stdlib, no new dependency)
- translation failures (any exception raised inside `translator.py` during the run, caught and logged, not swallowed)

Aggregated into:
- one row per fixture (language, doc-type match ✓/✗, clause recall %, red-flag P/R, evidence-span ✓/✗, latency ms)
- one summary row per language (mean/median/P95 latency, doc-type accuracy %, clause recall %, red-flag P/R)
- one overall summary (total pass/fail/blocked, peak RAM across the whole run, model names + revisions pulled from the HF cache metadata)

### 5. Report generation (`tests/generate_offline_report.py`, new)
Renders `tests/offline_validation_report.pdf` via `reportlab`, structured as:
- Title, date, scope statement (which languages/doc types were tested, which weren't and why)
- **Test Results** — real `reportlab.Table`, per-language and overall, matching the "Test category / Total / Passed / Failed / Blocked / Evidence" shape from the management directive's Priority 6
- **Verification Evidence** — pointers to `tests/offline_validation_results.json` (raw data) and this run's log output, referenced by relative repo path (e.g. `ldv-backend/tests/offline_validation_results.json`), never an absolute `/home/...` link
- **Model Provenance** — model IDs + revisions/commit hashes as read from the local HF cache, proving which exact model snapshot was used
- **Decisions Required from Management** — e.g. sign-off on residual gaps (no OCR, socket-trap vs. kernel-level offline proof) and acceptance of the P0 status
- Status column per acceptance item: Not started / In progress / Implemented / Tested / Accepted / Blocked

## Testing

The harness's own correctness is the thing to verify first: `self_check()` in `run_offline_validation.py` (an `assert`-based check, no framework) proves the outbound-block actually blocks before any fixture runs — a false "offline" result would be worse than no result. Then the harness run itself, over all fixtures, is the acceptance test; its JSON output is the raw evidence and the PDF is the human-readable summary.

## Out of scope

Physical/kernel-level network isolation, Celery/Redis async queue (Priority 2), MFA completion (Priority 3), TLS/infra validation (Priority 4), job-recovery heartbeats (Priority 5) — each gets its own spec once this one ships. Also out of scope: reformatting the existing dated `docs/YYYY-MM-DD.md` daily reports — that's a separate, smaller process fix, not part of this deliverable.
