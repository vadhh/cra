"""Self-check for worker.py background task queues and status tracking (CR-10)."""
import importlib
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import worker


def test_needs_confirmation_below_absolute_threshold():
    dt = {"confidence": 0.50, "candidates": [{"confidence": 0.50}, {"confidence": 0.10}]}
    needs, reason = worker._needs_confirmation(dt)
    assert needs is True
    assert reason == "low_confidence"


def test_needs_confirmation_ambiguous_margin():
    # 76% vs 74%: clears the 0.70 confirmation threshold alone, but under the
    # 0.85 high-confidence threshold with only a 2% margin -- still ambiguous.
    dt = {"confidence": 0.76, "candidates": [{"confidence": 0.76}, {"confidence": 0.74}]}
    needs, reason = worker._needs_confirmation(dt)
    assert needs is True
    assert reason == "ambiguous_margin"


def test_needs_confirmation_keyword_nli_disagreement():
    dt = {
        "confidence": 0.90,
        "candidates": [{"confidence": 0.90}, {"confidence": 0.05}],
        "override_applied": True,
        "override_reason": "generic_to_specific",
    }
    needs, reason = worker._needs_confirmation(dt)
    assert needs is True
    assert reason == "keyword_nli_disagreement"


def test_needs_confirmation_high_confidence_wide_margin_passes():
    dt = {"confidence": 0.92, "candidates": [{"confidence": 0.92}, {"confidence": 0.05}]}
    needs, reason = worker._needs_confirmation(dt)
    assert needs is False
    assert reason is None


def test_needs_confirmation_draft_profile_gates_despite_high_confidence():
    # High confidence alone isn't enough for a profile the registry hasn't
    # empirically validated yet -- draft status must force confirmation.
    dt = {"confidence": 0.97, "candidates": [{"confidence": 0.97}, {"confidence": 0.02}]}
    profile = {"id": "mining_agreement", "classifier": {"status": "draft"}}
    needs, reason = worker._needs_confirmation(dt, profile=profile)
    assert needs is True
    assert reason == "draft_profile"


def test_needs_confirmation_validated_profile_not_gated_by_status():
    dt = {"confidence": 0.97, "candidates": [{"confidence": 0.97}, {"confidence": 0.02}]}
    profile = {"id": "employment_contract", "classifier": {"status": "validated"}}
    needs, reason = worker._needs_confirmation(dt, profile=profile)
    assert needs is False
    assert reason is None


def test_needs_confirmation_no_profile_resolved_falls_back_to_confidence_checks():
    # profile=None (the default) preserves prior behavior -- unresolved
    # profile shouldn't itself force a gate, confidence checks still apply.
    dt = {"confidence": 0.92, "candidates": [{"confidence": 0.92}, {"confidence": 0.05}]}
    needs, reason = worker._needs_confirmation(dt)
    assert needs is False
    assert reason is None


def test_classifier_thresholds_env_overridable():
    os.environ["LDV_CLASSIFIER_CONFIRMATION_THRESHOLD"] = "0.60"
    try:
        conf, high, margin = worker._classifier_thresholds()
        assert conf == 0.60
    finally:
        os.environ.pop("LDV_CLASSIFIER_CONFIRMATION_THRESHOLD", None)


def test_worker_flow():
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["LDV_DB_PATH"] = db_path
    os.environ.pop("LDV_ENCRYPTION_KEY", None)

    import database
    importlib.reload(database)
    database.init_db()

    # Mock app pipeline methods to avoid loading heavy PyTorch models in test
    import app
    _orig_run_analysis = app._run_analysis
    app._run_analysis = lambda text, jurisdiction, lang: {
        "layer1": {},
        "layer2": {"document_type": {"label": "NDA"}},
        "layer3": {"score": 12, "label": "LOW"},
    }

    import worker
    importlib.reload(worker)

    try:
        # Save dummy document
        doc_id = database.save_document("test.txt", "s.txt", "/tmp/s.txt", 10, ".txt", "EN", "extracted text content")

        # Create a queued analysis
        pid = database.save_analysis(doc_id, None, None, None, None, None, status="queued")

        res = database.get_result(pid)
        assert res["status"] == "queued"
        assert res["result_json"] is None

        # Submit the job
        worker.submit_job(pid, "extracted text content", "EN", False)

        # Wait for completion (it should run in background)
        timeout = 5.0
        start = time.time()
        while time.time() - start < timeout:
            res = database.get_result(pid)
            if res["status"] in ("completed", "failed"):
                break
            time.sleep(0.1)

        assert res["status"] == "completed"
        assert res["risk_score"] == 12
        assert res["risk_label"] == "LOW"
        assert res["document_type"] == "NDA"
        assert res["result_json"] is not None

        # Test Failure case
        pid_fail = database.save_analysis(doc_id, None, None, None, None, None, status="queued")

        # Cause failure in the mock
        def fail_run(text, jurisdiction, lang):
            raise ValueError("Pipeline crashed")

        app._run_analysis = fail_run

        # Submit failed job
        worker.submit_job(pid_fail, "some content", "EN", False)

        # Wait for failure
        start = time.time()
        while time.time() - start < timeout:
            res = database.get_result(pid_fail)
            if res["status"] in ("completed", "failed"):
                break
            time.sleep(0.1)

        assert res["status"] == "failed"
        assert "Pipeline crashed" in res["error_message"]
    finally:
        # Clean up
        app._run_analysis = _orig_run_analysis
        os.remove(db_path)

if __name__ == "__main__":
    test_needs_confirmation_below_absolute_threshold()
    test_needs_confirmation_ambiguous_margin()
    test_needs_confirmation_keyword_nli_disagreement()
    test_needs_confirmation_high_confidence_wide_margin_passes()
    test_needs_confirmation_draft_profile_gates_despite_high_confidence()
    test_needs_confirmation_validated_profile_not_gated_by_status()
    test_needs_confirmation_no_profile_resolved_falls_back_to_confidence_checks()
    test_classifier_thresholds_env_overridable()
    test_worker_flow()
    print("test_worker OK")
