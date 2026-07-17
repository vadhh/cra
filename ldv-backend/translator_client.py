import os
import logging
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)

# ponytail: single REST call; no class, no in-process detect/status beyond a
# best-effort health probe. External translation is DISABLED BY DEFAULT.
# Enable by setting LIGHTML_TRANSLATOR_URL + EXTERNAL_TRANSLATION_DISABLED=0.
# ponytail: ceiling — if microservice is down, returns original text (no retry).
#
# SAFETY (2026-07-16 management review, Priority 5) — this module enforces
# what code CAN enforce: HTTPS by default (LDV_LIGHTML_ALLOW_INSECURE=1 to
# override for trusted local dev only), optional bearer auth, a payload size
# cap, and never logging request/response body content. It CANNOT verify
# from code alone that LIGHTML_TRANSLATOR_URL actually points to a genuinely
# internal/protected host rather than a public third party, that its TLS
# certificate is trustworthy, or that LDV_LIGHTML_API_KEY is actually
# provisioned against that service — those require ops/infra confirmation
# before EXTERNAL_TRANSLATION_DISABLED is set to 0 anywhere real.

_MAX_CHARS_DEFAULT = 50_000


def _base_url() -> str:
    return os.getenv("LIGHTML_TRANSLATOR_URL", "").strip()


def _auth_headers() -> dict:
    key = os.getenv("LDV_LIGHTML_API_KEY", "")
    return {"Authorization": f"Bearer {key}"} if key else {}


def translate_via_microservice(text: str, src_lang: str) -> str:
    if not text.strip():
        return text
    # External translation guard: disabled unless explicitly enabled
    if os.getenv("EXTERNAL_TRANSLATION_DISABLED", "1") == "1":
        logger.debug("External translation disabled (EXTERNAL_TRANSLATION_DISABLED=1); returning original text.")
        return text
    url = _base_url()
    if not url:
        logger.debug("LIGHTML_TRANSLATOR_URL not set; skipping external translation.")
        return text
    if not url.lower().startswith("https://") and os.getenv("LDV_LIGHTML_ALLOW_INSECURE", "0") != "1":
        logger.warning(
            "LIGHTML_TRANSLATOR_URL is not https:// and LDV_LIGHTML_ALLOW_INSECURE "
            "is unset -- refusing to send contract text in cleartext. Set "
            "LDV_LIGHTML_ALLOW_INSECURE=1 only for trusted local dev."
        )
        return text
    max_chars = int(os.getenv("LDV_LIGHTML_MAX_CHARS", str(_MAX_CHARS_DEFAULT)))
    if len(text) > max_chars:
        logger.warning(
            "Text length %d exceeds LDV_LIGHTML_MAX_CHARS=%d; skipping external "
            "translation for this request (returning original text).",
            len(text), max_chars,
        )
        return text
    try:
        r = requests.post(
            url,
            json={"text": text, "source_lang": src_lang, "target_lang": "en", "sector": "Legal"},
            headers=_auth_headers(),
            timeout=120,
        )
        r.raise_for_status()
        return r.json().get("translated_text", text)
    except Exception as e:
        # Log only the exception type/message, never response body -- a
        # misbehaving service could echo submitted contract text back in an
        # error payload.
        logger.warning("Microservice translation failed: %s: %s", type(e).__name__, e)
        return text


def check_health(timeout: float = 3.0) -> dict:
    """Best-effort reachability probe for the /health endpoint surfacing in
    Flask's own /health route. Not a substitute for verifying the deployed
    service's actual security posture (see module docstring). Never raises."""
    if os.getenv("EXTERNAL_TRANSLATION_DISABLED", "1") == "1":
        return {"enabled": False, "reachable": None}
    url = _base_url()
    if not url:
        return {"enabled": False, "reachable": None}
    if not url.lower().startswith("https://") and os.getenv("LDV_LIGHTML_ALLOW_INSECURE", "0") != "1":
        # Same HTTPS-only gate as translate_via_microservice() -- otherwise
        # the bearer token in _auth_headers() would go out in cleartext.
        return {"enabled": True, "reachable": None}
    parsed = urlparse(url)
    health_url = f"{parsed.scheme}://{parsed.netloc}/health"
    try:
        r = requests.get(health_url, headers=_auth_headers(), timeout=timeout)
        return {"enabled": True, "reachable": r.ok}
    except Exception:
        return {"enabled": True, "reachable": False}
