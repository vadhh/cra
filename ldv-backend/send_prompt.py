import os

# Enforce offline mode if downloads not allowed
if os.getenv("LDV_DOWNLOAD_MODELS", "0") != "1":
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

import logging
import time
import concurrent.futures
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    StoppingCriteria,
    StoppingCriteriaList,
)

logger = logging.getLogger(__name__)

MODEL_ID = os.getenv("LDV_MODEL", "Qwen/Qwen3-1.7B")
GENERATION_TIMEOUT = int(os.getenv("LDV_GENERATION_TIMEOUT", "300"))  # seconds

_model = None
_tokenizer = None


def _load_model():
    global _model, _tokenizer
    if _model is None:
        logger.info("Loading model %s...", MODEL_ID)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32
        
        # ponytail: prevent blocking background threads with massive model downloads unless explicitly allowed
        download_allowed = os.getenv("LDV_DOWNLOAD_MODELS", "0") == "1"
        import hf_hub_connector
        qwen_cached = hf_hub_connector.is_model_cached(MODEL_ID)
        
        if not download_allowed and not qwen_cached:
            logger.warning("Model %s is not cached locally and LDV_DOWNLOAD_MODELS is not 1. Skipping download.", MODEL_ID)
            raise RuntimeError("Model not cached locally and downloads are disabled.")
            
        local_files_only = not download_allowed

        _tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, local_files_only=local_files_only)
        m = AutoModelForCausalLM.from_pretrained(MODEL_ID, torch_dtype=dtype, local_files_only=local_files_only).to(device)
        m.training = False
        _model = m
        logger.info("Model loaded on %s.", device)
    return _model, _tokenizer


def query_llm(prompt):
    try:
        model, tokenizer = _load_model()
        messages = [{"role": "user", "content": prompt}]

        try:
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False,
            )
        except TypeError:
            text = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )

        inputs = tokenizer(text, return_tensors="pt").to(model.device)

        # Wall-clock stop inside generate() itself — generation halts at the
        # deadline instead of burning CPU after the caller has given up.
        class _Deadline(StoppingCriteria):
            def __init__(self, seconds):
                self.deadline = time.monotonic() + seconds

            def __call__(self, input_ids, scores, **kwargs):
                return time.monotonic() >= self.deadline

        def _generate():
            with torch.no_grad():
                return model.generate(
                    **inputs,
                    max_new_tokens=512,
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id,
                    stopping_criteria=StoppingCriteriaList(
                        [_Deadline(GENERATION_TIMEOUT)]
                    ),
                )

        # No `with` block: ThreadPoolExecutor.__exit__ calls shutdown(wait=True),
        # which would block until generation finishes even after a timeout.
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        try:
            future = executor.submit(_generate)
            # Grace period past the in-generate deadline (per-token overshoot)
            output_ids = future.result(timeout=GENERATION_TIMEOUT + 30)
        except concurrent.futures.TimeoutError:
            logger.error(
                "Inference timed out after %d seconds (LDV_GENERATION_TIMEOUT).",
                GENERATION_TIMEOUT,
            )
            return None
        finally:
            executor.shutdown(wait=False)

        new_tokens = output_ids[0][inputs["input_ids"].shape[1]:]
        return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

    except Exception as e:
        logger.error("Inference failed: %s", e)
        return None
