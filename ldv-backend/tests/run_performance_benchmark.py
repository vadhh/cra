"""Performance benchmark: cold-start vs warm latency, P50/P95/max, broken out
by language and file size (per the 2026-07-06 external review's explicit
request for "real cold-start, warm, P50 and P95 latency measurements by
language and file type").

Cold start = wall-clock time for a brand-new Python process (paying full
torch/transformers import + model-load cost) to complete exactly one
analysis, measured from the parent process around a subprocess launch — the
number a user actually experiences on the very first request after a
server/worker restart.

Warm = latency of repeated analysis calls in an already-loaded process
(models cached), which is what every request after the first one sees.

Run: python3 tests/run_performance_benchmark.py
Writes: tests/performance_benchmark_results.json
"""
import os
import sys
import json
import time
import subprocess
import statistics
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, BACKEND_DIR)

os.environ["LDV_REMOTE_TRANSLATION"] = "local"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from offline_metrics import percentile

FIXTURES_DIR = Path(HERE) / "fixtures"
RESULTS_PATH = Path(HERE) / "performance_benchmark_results.json"

REPEATS_PER_CASE = 5

# One representative fixture per language for cold-start measurement.
COLD_START_CASES = [
    {"lang": "en", "path": "pdf/03_nda_en.pdf"},
    {"lang": "id", "path": "pdf/01_employment_id.pdf"},
    {"lang": "fr", "path": "pdf/02_lease_be.pdf"},
    {"lang": "nl", "path": "docx/03_nda_nl.docx"},
]

# Warm-run cases: (language, file_type, size_bucket, path). "large" cases are
# synthetic — the fixture set has no naturally large document, so a 6x
# repetition of a real small fixture (preserving one-clause-per-line
# structure) stands in as a stress case for translation/NLI at scale.
WARM_CASES = [
    {"lang": "en", "file_type": "pdf", "size": "small", "path": "pdf/03_nda_en.pdf"},
    {"lang": "en", "file_type": "pdf", "size": "small", "path": "pdf/05_brochure_en.pdf"},
    {"lang": "id", "file_type": "pdf", "size": "small", "path": "pdf/01_employment_id.pdf"},
    {"lang": "id", "file_type": "txt", "size": "small", "path": "txt/12_high_risk_unilateral_id.txt"},
    {"lang": "fr", "file_type": "pdf", "size": "small", "path": "pdf/02_lease_be.pdf"},
    {"lang": "fr", "file_type": "docx", "size": "small", "path": "docx/02_employment_fr.docx"},
    {"lang": "nl", "file_type": "docx", "size": "small", "path": "docx/03_nda_nl.docx"},
    {"lang": "nl", "file_type": "txt", "size": "small", "path": "txt/13_medium_risk_lease_nl.txt"},
]

LARGE_SOURCE_FOR_LANG = {
    "en": "pdf/03_nda_en.pdf",
    "id": "pdf/01_employment_id.pdf",
    "fr": "pdf/02_lease_be.pdf",
    "nl": "docx/03_nda_nl.docx",
}


def _extract_text(file_path, extract_pdf, extract_docx, extract_txt):
    ext = file_path.suffix.lower()
    data = file_path.read_bytes()
    if ext == ".pdf":
        return extract_pdf(data)
    elif ext == ".docx":
        return extract_docx(data)
    return extract_txt(data)


def _make_large_text(base_text: str, repeats: int = 6) -> str:
    """Repeat a small fixture's lines with a section marker, preserving the
    one-clause-per-line structure the translator/paragraph-splitter rely on."""
    sections = [f"Section {i + 1}\n{base_text}" for i in range(repeats)]
    return "\n".join(sections)


def _run_cold_start_subprocess(lang: str, path: str) -> float:
    """Launch a brand-new interpreter, run one analysis, return total
    wall-clock time (process launch -> completion) in milliseconds."""
    script = f"""
import os, sys, time
os.environ["LDV_REMOTE_TRANSLATION"] = "local"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
sys.path.insert(0, {HERE!r})
sys.path.insert(0, {BACKEND_DIR!r})
from app import _run_analysis, _extract_pdf, _extract_docx, _extract_txt
from detector.detector_jurisdiction import detect_jurisdiction
from langdetect import detect
from pathlib import Path

file_path = Path({str(FIXTURES_DIR)!r}) / {path!r}
ext = file_path.suffix.lower()
data = file_path.read_bytes()
if ext == ".pdf":
    text = _extract_pdf(data)
elif ext == ".docx":
    text = _extract_docx(data)
else:
    text = data.decode("utf-8", errors="ignore")

try:
    lang = detect(text)
except Exception:
    lang = "unknown"
jurisdiction = detect_jurisdiction(text)
_run_analysis(text, jurisdiction, lang)
print("DONE")
"""
    t0 = time.perf_counter()
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, text=True, timeout=180,
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000
    if "DONE" not in result.stdout:
        raise RuntimeError(f"cold-start subprocess failed for {lang}/{path}: {result.stderr[-2000:]}")
    return elapsed_ms


def _stats(latencies: list) -> dict:
    return {
        "n": len(latencies),
        "mean_ms": round(statistics.mean(latencies), 1),
        "median_ms": round(statistics.median(latencies), 1),
        "p95_ms": round(percentile(latencies, 95), 1),
        "max_ms": round(max(latencies), 1),
        "min_ms": round(min(latencies), 1),
    }


def main():
    print("=== Phase 1: cold start (fresh process per language) ===")
    cold_start = {}
    for case in COLD_START_CASES:
        ms = _run_cold_start_subprocess(case["lang"], case["path"])
        cold_start[case["lang"]] = {"path": case["path"], "latency_ms": round(ms, 1)}
        print(f"  {case['lang']}: {ms:.1f} ms (fixture: {case['path']})")

    print("\n=== Phase 2: warm runs (already-loaded process, repeated calls) ===")
    from app import _run_analysis, _extract_pdf, _extract_docx, _extract_txt
    from detector.detector_jurisdiction import detect_jurisdiction
    from langdetect import detect

    # Warm up every model once before measuring, so the first *measured*
    # warm-run case for each language isn't accidentally still cold.
    for lang, path in LARGE_SOURCE_FOR_LANG.items():
        text = _extract_text(FIXTURES_DIR / path, _extract_pdf, _extract_docx, _extract_txt)
        jurisdiction = detect_jurisdiction(text)
        _run_analysis(text, jurisdiction, lang)
    print("  (warm-up pass complete)")

    per_case_results = []
    by_language: dict[str, list] = {}
    by_file_type: dict[str, list] = {}
    by_size: dict[str, list] = {}

    def _record(lang, file_type, size, latencies):
        by_language.setdefault(lang, []).extend(latencies)
        by_file_type.setdefault(file_type, []).extend(latencies)
        by_size.setdefault(size, []).extend(latencies)

    for case in WARM_CASES:
        file_path = FIXTURES_DIR / case["path"]
        text = _extract_text(file_path, _extract_pdf, _extract_docx, _extract_txt)
        jurisdiction = detect_jurisdiction(text)
        latencies = []
        for _ in range(REPEATS_PER_CASE):
            t0 = time.perf_counter()
            _run_analysis(text, jurisdiction, case["lang"])
            latencies.append((time.perf_counter() - t0) * 1000)
        stats = _stats(latencies)
        per_case_results.append({**case, **stats})
        _record(case["lang"], case["file_type"], case["size"], latencies)
        print(f"  {case['path']}: median={stats['median_ms']}ms p95={stats['p95_ms']}ms (n={stats['n']})")

    for lang, path in LARGE_SOURCE_FOR_LANG.items():
        base_text = _extract_text(FIXTURES_DIR / path, _extract_pdf, _extract_docx, _extract_txt)
        large_text = _make_large_text(base_text, repeats=6)
        jurisdiction = detect_jurisdiction(large_text)
        latencies = []
        for _ in range(REPEATS_PER_CASE):
            t0 = time.perf_counter()
            _run_analysis(large_text, jurisdiction, lang)
            latencies.append((time.perf_counter() - t0) * 1000)
        stats = _stats(latencies)
        case = {"lang": lang, "file_type": Path(path).suffix.lstrip("."), "size": "large",
                "path": f"synthetic:6x:{path}", "chars": len(large_text)}
        per_case_results.append({**case, **stats})
        _record(lang, case["file_type"], "large", latencies)
        print(f"  synthetic large {lang} ({len(large_text)} chars): "
              f"median={stats['median_ms']}ms p95={stats['p95_ms']}ms (n={stats['n']})")

    results = {
        "repeats_per_case": REPEATS_PER_CASE,
        "cold_start": cold_start,
        "warm_by_case": per_case_results,
        "warm_by_language": {k: _stats(v) for k, v in by_language.items()},
        "warm_by_file_type": {k: _stats(v) for k, v in by_file_type.items()},
        "warm_by_size": {k: _stats(v) for k, v in by_size.items()},
    }
    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nResults written to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
