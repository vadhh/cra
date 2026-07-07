from generate_offline_report import generate_report


def test_generates_valid_pdf_from_synthetic_results(tmp_path):
    synthetic = {
        "self_check_passed": True,
        "config": {
            "LDV_REMOTE_TRANSLATION": "local",
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "started_at": "2026-07-06T00:00:00",
            "finished_at": "2026-07-06T00:10:00",
        },
        "model_provenance": [{"name": "Helsinki-NLP/opus-mt-fr-en", "revision": "abc123"}],
        "translation_failures": [],
        "peak_rss_mb": 512.0,
        "fixtures": [
            {"path": "pdf/01_employment_id.pdf", "status": "PASS", "error": None,
             "document_type_detected": "employment contract"},
            {"path": "negative/some_malformed.pdf", "status": "ERROR",
             "error": "extraction failed: invalid PDF structure"},
        ],
        "by_language": {
            "id": {"total": 1, "passed": 1, "failed": 0, "doc_type_accuracy_pct": 100.0,
                   "clause_recall_pct": 100.0, "latency_mean_ms": 500.0,
                   "latency_median_ms": 500.0, "latency_p95_ms": 500.0},
        },
        "overall": {"total": 1, "passed": 1, "failed": 0, "blocked": 0},
    }
    out_path = tmp_path / "report.pdf"
    generate_report(synthetic, out_path)
    assert out_path.exists()
    assert out_path.read_bytes()[:4] == b"%PDF"
    assert out_path.stat().st_size > 1000
