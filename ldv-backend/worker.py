"""worker.py — lightweight in-process background worker queue using thread pools (CR-10)."""
from __future__ import annotations

import logging
import os
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Single worker thread to avoid concurrent PyTorch/LLM execution thrashing CPU
_executor = ThreadPoolExecutor(max_workers=1)


def _classifier_thresholds() -> tuple[float, float, float]:
    """(confirmation_threshold, high_confidence_threshold, minimum_margin), env-overridable.

    Defaults match the original 0.70 gate; read fresh (not cached) so tests
    can override os.environ per-case.
    """
    conf = float(os.getenv("LDV_CLASSIFIER_CONFIRMATION_THRESHOLD", "0.70"))
    high = float(os.getenv("LDV_CLASSIFIER_HIGH_CONFIDENCE_THRESHOLD", "0.85"))
    margin = float(os.getenv("LDV_CLASSIFIER_MINIMUM_MARGIN", "0.15"))
    return conf, high, margin


def _needs_confirmation(dt: dict, profile: dict | None = None) -> tuple[bool, str | None]:
    """Whether a Layer-2 classifier result should be gated for manual confirmation.

    Per the 2026-07-16 management review (Priority 3), evaluates more than the
    single absolute-confidence check:
    - confidence below LDV_CLASSIFIER_CONFIRMATION_THRESHOLD -> "low_confidence"
    - confidence below LDV_CLASSIFIER_HIGH_CONFIDENCE_THRESHOLD *and* the top
      two NLI candidates are within LDV_CLASSIFIER_MINIMUM_MARGIN of each other
      -> "ambiguous_margin" (e.g. 76% vs 74%: 76% clears the confirmation
      threshold alone, but the result is still ambiguous)
    - the keyword pass disagreed with NLI, or a generic label lost to a more
      specific keyword match (classify_document_type's override_reason)
      -> "keyword_nli_disagreement"

    Per a later review, also gates on registry status regardless of
    confidence: an automatically-classified `draft` profile (or a resolved
    profile with no classifier config at all) hasn't been empirically
    validated yet, so a high-confidence NLI score doesn't mean the profile's
    required-clause set or scoring behavior is trustworthy -> "draft_profile".
    This check only runs when the caller passes a resolved `profile` --
    the caller only does so for detection_source == "classifier", so a
    manually-selected profile is never re-gated here: an explicit human
    choice already satisfies "confirmation or manual selection".

    Manual selection is handled by the caller (only gates when
    detection_source == "classifier"); retry-budget exhaustion is already
    enforced by database._MAX_RETRIES in retry_analysis().
    """
    if profile is not None:
        status = (profile.get("classifier") or {}).get("status")
        if status != "validated":
            return True, "draft_profile"

    confidence = dt.get("confidence")
    if confidence is None:
        return False, None

    conf_threshold, high_threshold, min_margin = _classifier_thresholds()

    if confidence < conf_threshold:
        return True, "low_confidence"

    if confidence < high_threshold:
        candidates = dt.get("candidates") or []
        if len(candidates) >= 2:
            top_conf = candidates[0].get("confidence", confidence)
            second_conf = candidates[1].get("confidence", 0.0)
            if (top_conf - second_conf) < min_margin:
                return True, "ambiguous_margin"

    if dt.get("override_applied") and dt.get("override_reason") in ("keyword_match", "generic_to_specific"):
        return True, "keyword_nli_disagreement"

    return False, None


def _run_job(public_id: str, text: str, lang: str, explain: bool, policy_name: str | None = None, override_jurisdiction: str | None = None, override_type: str | None = None) -> None:
    import database
    from app import _run_analysis, translate_text, logger as app_logger
    from detector.detector_explain import layer4_explain
    import time
    import traceback
    import inspect

    try:
        database.update_analysis(public_id, status="processing", progress_pct=20, progress_stage="extracting")
        t_start = time.monotonic()

        # Run core L1-L3 analysis
        if override_jurisdiction:
            jurisdiction = override_jurisdiction
        else:
            from detector.detector_jurisdiction import detect_jurisdiction
            jurisdiction = detect_jurisdiction(text)
        
        database.update_analysis(public_id, status="processing", progress_pct=40, progress_stage="classifying")
        
        # Check signature to support 3-arg mocks in tests
        sig = inspect.signature(_run_analysis)
        kwargs = {}
        if "policy_name" in sig.parameters:
            kwargs["policy_name"] = policy_name
        if "override_type" in sig.parameters:
            kwargs["override_type"] = override_type

        database.update_analysis(public_id, status="processing", progress_pct=60, progress_stage="analyzing")
        result = _run_analysis(text, jurisdiction, lang, **kwargs)
        database.update_analysis(public_id, status="processing", progress_pct=80, progress_stage="scoring")

        # Run L4 optional LLM explanation
        if explain:
            database.update_analysis(public_id, status="processing", progress_pct=85, progress_stage="reasoning")
            layer1 = result.get("layer1")
            layer2 = result.get("layer2")
            layer3 = result.get("layer3")
            analysis_text = text
            if lang not in ("en", "unknown"):
                try:
                    analysis_text = translate_text(text, "en", src_lang=lang)
                except Exception:
                    pass
            result["layer4"] = layer4_explain(
                analysis_text, jurisdiction=jurisdiction,
                layer1=layer1, layer2=layer2, layer3=layer3,
            )

        database.update_analysis(public_id, status="processing", progress_pct=95, progress_stage="preparing")

        elapsed = round(time.monotonic() - t_start, 2)
        layer3_data = result.get("layer3", {})\
            if not result.get("layer3", {}).get("skipped") else {}
        layer2_data = result.get("layer2", {}) or {}
        dt = layer2_data.get("document_type")
        doc_type_str = dt.get("label") if isinstance(dt, dict) else dt

        # Phase 2 (P6): extract profile provenance from layer2 detector output
        detection_confidence = dt.get("confidence") if isinstance(dt, dict) else None
        detection_source = "baseline"
        if override_type:
            detection_source = "user_override"
        elif isinstance(dt, dict) and dt.get("source") not in (None, ""):
            detection_source = "classifier"

        # Resolve profile_id and profile_version from registry
        _pid = None
        _pver = None
        p = None
        try:
            from detector.profile_registry import detect_profile
            p = detect_profile(doc_type_str or "")
            if p:
                _pid = p["id"]
                _pver = p["version"]
                detection_source = detection_source  # keep user_override if set
        except Exception:
            pass

        # Phase 3 (S2): persist score breakdown and policy_version
        _breakdown = layer3_data.get("breakdown") if layer3_data else None
        _policy_ver = layer3_data.get("policy_version") if layer3_data else None

        # layer3_data can be {} when non-contract path used
        _score = layer3_data.get("score") if layer3_data else None
        _label = layer3_data.get("label") if layer3_data else None

        final_status = "completed"
        final_error = None
        if detection_source == "classifier":
            needs_confirmation, gate_reason = _needs_confirmation(dt if isinstance(dt, dict) else {}, profile=p)
            if needs_confirmation:
                final_status = "retryable"
                # Kept as the stable "low_confidence" value: app.py's GET /result
                # and index.html's frontend gate the candidate-selection UI on
                # this exact string regardless of which check actually tripped.
                final_error = "low_confidence"
                app_logger.info(
                    "ASYNC WORKER: confirmation gate triggered id=%s reason=%s confidence=%s",
                    public_id, gate_reason, detection_confidence,
                )

        database.update_analysis(
            public_id=public_id,
            status=final_status,
            error_message=final_error,
            jurisdiction=jurisdiction,
            document_type=doc_type_str,
            risk_score=_score,
            risk_label=_label,
            result=result,
            progress_pct=100,
            progress_stage="preparing",
            profile_id=_pid,
            profile_version=_pver,
            detection_source=detection_source,
            detection_confidence=detection_confidence,
            score_breakdown=_breakdown,
            policy_version=_policy_ver,
        )

        if final_status == "completed":
            app_logger.info(
                "ASYNC WORKER: completed id=%s jurisdiction=%s risk=%s/%s time=%.2fs",
                public_id, jurisdiction, layer3_data.get("score"), layer3_data.get("label"), elapsed
            )
        else:
            app_logger.info(
                "ASYNC WORKER: interrupted (low classification confidence) id=%s time=%.2fs",
                public_id, elapsed
            )
    except Exception as e:
        err_msg = f"{str(e)}\n{traceback.format_exc()}"
        app_logger.error("ASYNC WORKER ERROR: id=%s err=%s", public_id, err_msg)
        try:
            database.update_analysis(public_id, status="failed", error_message=err_msg, progress_pct=100, progress_stage="preparing")
        except Exception as db_err:
            app_logger.critical("ASYNC WORKER DB UPDATE FAILED: id=%s err=%s", public_id, db_err)


def submit_job(public_id: str, text: str, lang: str, explain: bool, policy_name: str | None = None, override_jurisdiction: str | None = None, override_type: str | None = None) -> None:
    """Submit a contract analysis job to the background worker pool."""
    _executor.submit(_run_job, public_id, text, lang, explain, policy_name, override_jurisdiction, override_type)
