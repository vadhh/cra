"""worker.py — lightweight in-process background worker queue using thread pools (CR-10)."""
from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Single worker thread to avoid concurrent PyTorch/LLM execution thrashing CPU
_executor = ThreadPoolExecutor(max_workers=1)


def _run_job(public_id: str, text: str, lang: str, explain: bool) -> None:
    import database
    from app import _run_analysis, translate_text, logger as app_logger
    from detector.detector_explain import layer4_explain
    import time
    import traceback

    try:
        database.update_analysis(public_id, status="running")
        t_start = time.monotonic()

        # Run core L1-L3 analysis
        from detector.detector_jurisdiction import detect_jurisdiction
        jurisdiction = detect_jurisdiction(text)
        result = _run_analysis(text, jurisdiction, lang)

        # Run L4 optional LLM explanation
        if explain:
            layer1 = result.get("layer1")
            layer2 = result.get("layer2")
            layer3 = result.get("layer3")
            analysis_text = text
            if lang not in ("en", "unknown"):
                try:
                    analysis_text = translate_text(text, "en")
                except Exception:
                    pass
            result["layer4"] = layer4_explain(
                analysis_text, jurisdiction=jurisdiction,
                layer1=layer1, layer2=layer2, layer3=layer3,
            )

        elapsed = round(time.monotonic() - t_start, 2)
        layer3_data = result.get("layer3", {})
        layer2_data = result.get("layer2", {}) or {}
        dt = layer2_data.get("document_type")
        doc_type_str = dt.get("label") if isinstance(dt, dict) else dt

        database.update_analysis(
            public_id=public_id,
            status="completed",
            jurisdiction=jurisdiction,
            document_type=doc_type_str,
            risk_score=layer3_data.get("score"),
            risk_label=layer3_data.get("label"),
            result=result
        )

        app_logger.info(
            "ASYNC WORKER: completed id=%s jurisdiction=%s risk=%s/%s time=%.2fs",
            public_id, jurisdiction, layer3_data.get("score"), layer3_data.get("label"), elapsed
        )
    except Exception as e:
        err_msg = f"{str(e)}\n{traceback.format_exc()}"
        app_logger.error("ASYNC WORKER ERROR: id=%s err=%s", public_id, err_msg)
        try:
            database.update_analysis(public_id, status="failed", error_message=err_msg)
        except Exception as db_err:
            app_logger.critical("ASYNC WORKER DB UPDATE FAILED: id=%s err=%s", public_id, db_err)


def submit_job(public_id: str, text: str, lang: str, explain: bool) -> None:
    """Submit a contract analysis job to the background worker pool."""
    _executor.submit(_run_job, public_id, text, lang, explain)
