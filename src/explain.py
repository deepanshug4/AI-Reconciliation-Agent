"""
LLM explanation layer.

Takes a single exception record and returns a plain-English explanation
plus a suggested resolution. Designed to fail gracefully: if no API key
is set or the API call fails, it returns a deterministic fallback message
so the app never crashes.
"""

import os
from dotenv import load_dotenv

load_dotenv()

_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Lazy import so the app runs even if anthropic isn't installed/configured.
_client = None


def _get_client():
    global _client
    if _client is None:
        from anthropic import Anthropic
        _client = Anthropic(api_key=_API_KEY)
    return _client


def _fallback_explanation(exception_row: dict) -> str:
    """Deterministic explanation used when the LLM is unavailable."""
    reason = exception_row.get("reason", "Unknown discrepancy")
    return (f"{reason}. Suggested action: verify the record in the source "
            f"system and confirm whether it should be added, removed, or corrected.")


def explain_exception(exception_row: dict) -> str:
    """
    Return an AI-generated explanation for one exception.
    Falls back to a deterministic message if the API is unavailable.
    """
    if not _API_KEY:
        return _fallback_explanation(exception_row)

    prompt = (
        "You are a financial reconciliation assistant. "
        "Given this exception record, explain in 1-2 sentences what likely "
        "went wrong and suggest a concrete resolution step. "
        "Be concise, factual, and professional.\n\n"
        f"Exception record:\n{exception_row}"
    )

    try:
        client = _get_client()
        # -----------------------------------------------------------------
        # VERIFY THIS BLOCK against the current Anthropic Python SDK docs.
        # Model names and the .messages.create signature change over time.
        # -----------------------------------------------------------------
        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text.strip()
    except Exception as e:
        # Never let an API issue break the app.
        return f"{_fallback_explanation(exception_row)} (AI note unavailable: {e})"