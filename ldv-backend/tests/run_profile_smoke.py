"""tests/run_profile_smoke.py — Priority 6 from the 2026-07-16 management
review: "run 56x3 smoke tests (manual-profile, auto-detection,
PDF-generation) as an immediate step before the full 168-fixture corpus
exists."

This is a CRASH/COVERAGE sweep across all 56 registry profiles, not an
accuracy validation -- correctness against real contract fixtures is
Ilham's 168-fixture corpus (docs/p7_catalogue_reconciliation.md, still
pending). Three checks per profile:

  1. manual -- force the profile the same way app.py's override_type does
               (document_type label pre-set, source=user_selected), then run
               the real L3 scorer. No ML calls -- fast.
  2. auto   -- run the real DistilBERT classifier against text built from the
               profile's own classifier.hypothesis/positive_keywords. Only
               asserts no exception and a label comes back -- NOT that it
               classifies correctly (that's the 168-fixture corpus's job).
  3. pdf    -- render a synthetic portal-shaped result through generate_pdf()
               and confirm it doesn't crash and contains the profile name.

Not part of the fast pytest suite -- check 2 loads DistilBERT and runs real
inference 56 times (~5-15s each on CPU), same tradeoff as run_benchmark.py.

Run: python3 tests/run_profile_smoke.py
"""
import os
import sys
import json
import time
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(HERE)
sys.path.insert(0, BACKEND_DIR)

import fitz  # PyMuPDF -- already a hard dependency, used by app.py for input extraction

from detector import profile_registry
from detector.detector_rules import layer1_analyze, evaluate_contract_type_requirements
from detector.detector_scorer import layer3_score
from detector.detector_distilbert import classify_document_type
from pdf_report import generate_pdf


def _pdf_text(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        return "".join(page.get_text() for page in doc)
    finally:
        doc.close()


def _synthetic_text(profile: dict) -> str:
    clf = profile.get("classifier") or {}
    keywords = clf.get("positive_keywords") or profile["aliases"]
    body = ". ".join(keywords) + ". " + clf.get("hypothesis", "")
    return f"{profile['display_name']}\n\n{body}\n\nThis agreement is entered into by the parties."


def check_manual(profile: dict) -> tuple[bool, str]:
    text = _synthetic_text(profile)
    try:
        layer1 = layer1_analyze(text, "Unknown")
        label = profile["display_name"].lower()
        layer2 = {
            "document_type": {"label": label, "confidence": 1.0, "source": "user_selected"},
            "flagged_clauses": [],
            "layer2_available": True,
        }
        result = layer3_score(layer1, layer2, lang="EN")
        req = evaluate_contract_type_requirements(layer1.get("clause_presence", []), label)
        if not req["matched_profile"]:
            return False, "registry did not resolve display_name back to this profile"
        if result.get("score") is None:
            return False, "layer3_score returned no score"
        return True, ""
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def check_auto(profile: dict) -> tuple[bool, str]:
    text = _synthetic_text(profile)
    try:
        result = classify_document_type(text)
        if not result.get("label"):
            return False, "classify_document_type returned no label (model unavailable?)"
        return True, ""
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def check_pdf(profile: dict) -> tuple[bool, str]:
    label = profile["display_name"].lower()
    result = {
        "language": "en",
        "jurisdiction": "Indonesia",
        "layer1": {"governing_law": "Indonesia", "venue": "Jakarta", "red_flags": [], "clause_presence": []},
        "layer2": {
            "document_type": {"label": label, "confidence": 0.81, "candidates": [{"label": label, "confidence": 0.81}], "source": "classifier"},
            "flagged_clauses": [],
        },
        "layer3": {"score": 50, "label": "MEDIUM", "breakdown": [{"reason": "smoke test", "points": 0}]},
    }
    try:
        pdf_bytes = generate_pdf(result)
        if len(pdf_bytes) < 500:
            return False, f"suspiciously small PDF ({len(pdf_bytes)} bytes)"
        text = _pdf_text(pdf_bytes)
        if profile["display_name"] not in text:
            return False, "display_name missing from rendered PDF"
        return True, ""
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def main() -> int:
    profiles = [profile_registry.profile_for(pid) for pid in profile_registry.all_profile_ids()]
    results = []
    t0 = time.monotonic()
    for i, profile in enumerate(profiles, 1):
        pid = profile["id"]
        m_ok, m_err = check_manual(profile)
        p_ok, p_err = check_pdf(profile)
        a_ok, a_err = check_auto(profile)
        print(f"[{i}/{len(profiles)}] {pid}: manual={'OK' if m_ok else 'FAIL'} pdf={'OK' if p_ok else 'FAIL'} auto={'OK' if a_ok else 'FAIL'}", flush=True)
        results.append({
            "profile_id": pid,
            "display_name": profile["display_name"],
            "classifier_status": (profile.get("classifier") or {}).get("status"),
            "manual": {"pass": m_ok, "error": m_err},
            "auto": {"pass": a_ok, "error": a_err},
            "pdf": {"pass": p_ok, "error": p_err},
        })

    elapsed = round(time.monotonic() - t0, 1)
    total_checks = len(results) * 3
    passed = sum(int(r["manual"]["pass"]) + int(r["auto"]["pass"]) + int(r["pdf"]["pass"]) for r in results)
    failed_rows = [r for r in results if not (r["manual"]["pass"] and r["auto"]["pass"] and r["pdf"]["pass"])]

    report_path = Path(HERE) / "profile_smoke_report.json"
    report_path.write_text(json.dumps({
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_profiles": len(results),
        "total_checks": total_checks,
        "passed": passed,
        "elapsed_seconds": elapsed,
        "results": results,
    }, indent=2))

    print(f"\n{passed}/{total_checks} checks passed across {len(results)} profiles ({elapsed}s)")
    if failed_rows:
        print(f"{len(failed_rows)} profile(s) had at least one failing check:")
        for r in failed_rows:
            for check in ("manual", "auto", "pdf"):
                if not r[check]["pass"]:
                    print(f"  - {r['profile_id']} [{check}]: {r[check]['error']}")
    print(f"Full report: {report_path}")
    return 0 if not failed_rows else 1


if __name__ == "__main__":
    sys.exit(main())
