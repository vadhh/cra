"""Hugging Face Hub programmatic connector.

Provides utilities for model download, caching status checks, and authentication.
"""
from __future__ import annotations

import logging
import os
import sys

logger = logging.getLogger(__name__)

# Try importing huggingface_hub; if not present, we will prompt how to install it.
try:
    import huggingface_hub
    from huggingface_hub import HfApi, login, snapshot_download
    HAS_HF_HUB = True
except ImportError:
    HAS_HF_HUB = False


def check_hf_hub_dependency() -> None:
    if not HAS_HF_HUB:
        sys.exit(
            "Error: 'huggingface_hub' package is required for this action.\n"
            "Please install it using: pip install huggingface_hub"
        )


def hf_login(token: str | None = None) -> bool:
    """Log in to Hugging Face Hub. Uses environment HF_TOKEN if token not provided."""
    check_hf_hub_dependency()
    tok = token or os.getenv("HF_TOKEN")
    if not tok:
        logger.warning("No Hugging Face token provided. Attempting public hub calls.")
        return False
    try:
        login(token=tok)
        logger.info("Successfully authenticated with Hugging Face Hub.")
        return True
    except Exception as e:
        logger.error("Hugging Face login failed: %s", e)
        return False


def is_model_cached(repo_id: str) -> bool:
    """Check if model repository cache exists locally."""
    hf_cache_dir = os.getenv("HF_HOME") or os.path.expanduser("~/.cache/huggingface")
    model_slug = f"models--{repo_id.replace('/', '--')}"
    target_path = os.path.join(hf_cache_dir, "hub", model_slug)
    return os.path.exists(target_path)


def download_repo_model(repo_id: str, token: str | None = None) -> str | None:
    """Download model repository snapshot from Hugging Face Hub."""
    check_hf_hub_dependency()
    
    # Try logging in if token or environment variable exists
    hf_login(token)
    
    logger.info("Starting Hugging Face Hub download for '%s'...", repo_id)
    try:
        # snapshot_download retrieves the entire repository (safetensors, configs, tokenizers)
        local_dir = snapshot_download(
            repo_id=repo_id,
            repo_type="model",
            token=token or os.getenv("HF_TOKEN")
        )
        logger.info("Successfully downloaded and cached model to: %s", local_dir)
        return local_dir
    except Exception as e:
        logger.error("Failed to download model '%s' from Hugging Face Hub: %s", repo_id, e)
        return None
