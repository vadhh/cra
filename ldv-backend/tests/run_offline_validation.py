"""Offline multilingual acceptance harness (Priority 1 acceptance requirement).

Proves EN/ID/FR/NL contract + non-contract analysis with zero outbound
network calls, using local Marian MT translation.

Run: python3 tests/run_offline_validation.py
Writes: tests/offline_validation_results.json
"""
import os
import sys
import json
import time
import logging
import resource
import statistics
from datetime import datetime, timezone
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, BACKEND_DIR)

# Must be set before importing transformers/torch/app — HF_HUB_OFFLINE and
# TRANSFORMERS_OFFLINE make from_pretrained() skip the network entirely and
# use the local cache, instead of attempting an HTTP HEAD check first (which
# the socket trap below would otherwise report as a spurious model-load failure).
os.environ["LDV_REMOTE_TRANSLATION"] = "local"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from offline_net_trap import enable_network_trap, disable_network_trap, self_check
from offline_metrics import compute_clause_metrics, percentile

FIXTURES_DIR = Path(HERE) / "fixtures"
RESULTS_PATH = Path(HERE) / "offline_validation_results.json"

_HF_CACHE = Path(os.path.expanduser("~/.cache/huggingface/hub"))
_MODELS_TO_REPORT = [
    "Helsinki-NLP/opus-mt-id-en",
    "Helsinki-NLP/opus-mt-fr-en",
    "Helsinki-NLP/opus-mt-nl-en",
    "typeform/distilbert-base-uncased-mnli",
]

OFFLINE_SUITE = [
    {"path": "pdf/01_employment_id.pdf", "expected": {
        "language": "id", "is_contract": True,
        "present_clauses": ["governing_law", "termination", "working_hours", "compensation"],
        "missing_clauses": ["jurisdiction_venue", "notice_period", "dispute_resolution"],
    }},
    {"path": "pdf/02_lease_be.pdf", "expected": {
        "language": "fr", "is_contract": True,
        "present_clauses": ["governing_law", "termination", "rent_amount", "security_deposit"],
        "missing_clauses": ["jurisdiction_venue", "lease_term", "maintenance_responsibility", "dispute_resolution"],
    }},
    {"path": "pdf/03_nda_en.pdf", "expected": {
        "language": "en", "is_contract": True,
        "present_clauses": ["governing_law", "termination", "confidentiality"],
        "missing_clauses": ["jurisdiction_venue", "return_of_materials", "dispute_resolution"],
    }},
    {"path": "docx/02_employment_fr.docx", "expected": {"language": "fr", "is_contract": True}},
    {"path": "docx/03_nda_nl.docx", "expected": {"language": "nl", "is_contract": True}},
    {"path": "txt/12_high_risk_unilateral_id.txt", "expected": {"language": "id", "is_contract": True}},
    {"path": "txt/13_medium_risk_lease_nl.txt", "expected": {"language": "nl", "is_contract": True}},
    {"path": "pdf/05_brochure_en.pdf", "expected": {"language": "en", "is_contract": False}},
    {"path": "docx/06_memo_fr.docx", "expected": {"language": "fr", "is_contract": False}},
    {"path": "docx/07_brochure_nl.docx", "expected": {"language": "nl", "is_contract": False}},
    {"path": "txt/16_notice_id.txt", "expected": {"language": "id", "is_contract": False}},
    {"path": "pdf/06_scanned_blank_en.pdf", "expected": {"scan_required": True}},
    {"path": "negative/empty.pdf", "expected": {"extraction_error": True}},
    {"path": "negative/fake.pdf", "expected": {"extraction_error": True}},
]


class _TranslationFailureCapture(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.failures = []

    def emit(self, record):
        msg = record.getMessage()
        if "failed" in msg.lower():
            self.failures.append(msg)


def _extract_text(file_path, extract_pdf, extract_docx, extract_txt):
    ext = file_path.suffix.lower()
    data = file_path.read_bytes()
    if ext == ".pdf":
        return extract_pdf(data)
    elif ext == ".docx":
        return extract_docx(data)
    else:
        return extract_txt(data)


def _model_provenance() -> list:
    provenance = []
    for name in _MODELS_TO_REPORT:
        folder = "models--" + name.replace("/", "--")
        ref_path = _HF_CACHE / folder / "refs" / "main"
        if ref_path.exists():
            provenance.append({"name": name, "revision": ref_path.read_text().strip()})
        else:
            provenance.append({"name": name, "revision": "NOT CACHED"})
    return provenance


def run_suite(self_check_passed: bool) -> dict:
    from app import _run_analysis, _extract_pdf, _extract_docx, _extract_txt
    from detector.detector_jurisdiction import detect_jurisdiction
    from langdetect import detect

    capture = _TranslationFailureCapture()
    logging.getLogger("translator").addHandler(capture)

    started_at = datetime.now(timezone.utc).isoformat()
    fixture_results = []
    by_language = {}

    try:
        for case in OFFLINE_SUITE:
            file_path = FIXTURES_DIR / case["path"]
            expected = case["expected"]
            entry = {"path": case["path"]}

            if expected.get("extraction_error"):
                try:
                    _extract_text(file_path, _extract_pdf, _extract_docx, _extract_txt)
                    entry["status"] = "FAIL"
                    entry["error"] = "expected extraction to raise, it did not"
                except Exception as e:
                    entry["status"] = "PASS"
                    entry["error"] = str(e)
                fixture_results.append(entry)
                continue

            if expected.get("scan_required"):
                text = _extract_text(file_path, _extract_pdf, _extract_docx, _extract_txt)
                scan_required_detected = not text.strip()
                entry["status"] = "PASS" if scan_required_detected else "FAIL"
                entry["scan_required_detected"] = scan_required_detected
                entry["error"] = None
                fixture_results.append(entry)
                continue

            # Normal-analysis path (real ML pipeline: extraction, language/
            # jurisdiction detection, _run_analysis, clause-metrics). Isolated
            # per-fixture so one bad fixture can't blow away every completed
            # result and lose the JSON evidence file entirely.
            try:
                text = _extract_text(file_path, _extract_pdf, _extract_docx, _extract_txt)
                try:
                    lang = detect(text)
                except Exception:
                    lang = "unknown"
                jurisdiction = detect_jurisdiction(text)

                t0 = time.perf_counter()
                analysis = _run_analysis(text, jurisdiction, lang)
                latency_ms = (time.perf_counter() - t0) * 1000

                lang_match = lang.lower() == expected["language"].lower()
                l2 = analysis.get("layer2") or {}
                doc_type_detected = (l2.get("document_type") or {}).get("label")
                is_contract_detected = doc_type_detected is not None and analysis.get("layer3", {}).get("skipped") is not True
                is_contract_match = is_contract_detected == expected["is_contract"]

                clause_metrics = {"tp": 0, "fp": 0, "tn": 0, "fn": 0, "details": []}
                if expected["is_contract"] and "present_clauses" in expected:
                    presence_list = analysis.get("layer1", {}).get("clause_presence", [])
                    presence_map = {c["clause_id"]: c["present"] for c in presence_list}
                    clause_metrics = compute_clause_metrics(
                        presence_map, expected.get("present_clauses", []), expected.get("missing_clauses", [])
                    )

                status = "PASS" if (
                    lang_match and is_contract_match
                    and clause_metrics["fp"] == 0 and clause_metrics["fn"] == 0
                ) else "FAIL"

                entry.update({
                    "language_expected": expected["language"],
                    "language_detected": lang,
                    "language_match": lang_match,
                    "is_contract_expected": expected["is_contract"],
                    "is_contract_detected": is_contract_detected,
                    "is_contract_match": is_contract_match,
                    "document_type_detected": doc_type_detected,
                    "clause_tp": clause_metrics["tp"],
                    "clause_fp": clause_metrics["fp"],
                    "clause_tn": clause_metrics["tn"],
                    "clause_fn": clause_metrics["fn"],
                    "latency_ms": round(latency_ms, 1),
                    "status": status,
                    "error": None,
                })

                lang_key = expected["language"]
                bucket = by_language.setdefault(lang_key, {
                    "latencies": [], "total": 0, "passed": 0, "type_correct": 0,
                    "clause_tp": 0, "clause_fp": 0, "clause_fn": 0,
                })
                bucket["latencies"].append(latency_ms)
                bucket["total"] += 1
                bucket["passed"] += 1 if status == "PASS" else 0
                bucket["type_correct"] += 1 if is_contract_match else 0
                bucket["clause_tp"] += clause_metrics["tp"]
                bucket["clause_fp"] += clause_metrics["fp"]
                bucket["clause_fn"] += clause_metrics["fn"]

                # Appended last: if anything above raises, this fixture's
                # entry was never added, so the except branch below appends
                # exactly one ERROR entry for it (no duplicates) and this
                # fixture's (nonexistent) latency/language data never reaches
                # by_language.
                fixture_results.append(entry)
            except Exception as e:
                fixture_results.append({"path": case["path"], "status": "ERROR", "error": str(e)})
                continue
    finally:
        # Guaranteed handler cleanup even if a fixture raises somewhere the
        # try/except above doesn't cover (e.g. before the loop starts).
        logging.getLogger("translator").removeHandler(capture)

    by_language_summary = {}
    for lang_key, bucket in by_language.items():
        lat = bucket["latencies"]
        recall_denom = bucket["clause_tp"] + bucket["clause_fn"]
        by_language_summary[lang_key] = {
            "total": bucket["total"],
            "passed": bucket["passed"],
            "failed": bucket["total"] - bucket["passed"],
            "doc_type_accuracy_pct": round(100 * bucket["type_correct"] / bucket["total"], 1) if bucket["total"] else 0.0,
            "clause_recall_pct": round(100 * bucket["clause_tp"] / recall_denom, 1) if recall_denom else None,
            "latency_mean_ms": round(statistics.mean(lat), 1) if lat else 0.0,
            "latency_median_ms": round(statistics.median(lat), 1) if lat else 0.0,
            "latency_p95_ms": round(percentile(lat, 95), 1) if lat else 0.0,
        }

    finished_at = datetime.now(timezone.utc).isoformat()
    peak_rss_mb = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)

    total = len(fixture_results)
    passed = sum(1 for r in fixture_results if r["status"] == "PASS")

    return {
        "self_check_passed": self_check_passed,
        "config": {
            "LDV_REMOTE_TRANSLATION": os.environ.get("LDV_REMOTE_TRANSLATION"),
            "HF_HUB_OFFLINE": os.environ.get("HF_HUB_OFFLINE"),
            "TRANSFORMERS_OFFLINE": os.environ.get("TRANSFORMERS_OFFLINE"),
            "started_at": started_at,
            "finished_at": finished_at,
        },
        "model_provenance": _model_provenance(),
        "translation_failures": capture.failures,
        "peak_rss_mb": peak_rss_mb,
        "fixtures": fixture_results,
        "by_language": by_language_summary,
        "overall": {"total": total, "passed": passed, "failed": total - passed, "blocked": 0},
    }


def main():
    ok = self_check()
    if not ok:
        disable_network_trap()
        raise SystemExit(
            "Network trap self-check FAILED — refusing to run, results would not prove offline operation"
        )
    print("Network trap self-check: PASS (outbound connect correctly blocked)")

    try:
        results = run_suite(ok)
    finally:
        disable_network_trap()

    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Results written to {RESULTS_PATH}")
    print(f"Overall: {results['overall']['passed']}/{results['overall']['total']} passed")


if __name__ == "__main__":
    main()
