"""Structural tests for the DeepSeek adapter — no network, no spend.

Mirrors the OpenAI adapter tests: verify protocol conformance, lazy
import, early failure on a missing key, and that the DeepSeek endpoint
defaults are wired up — without ever calling the real API.
"""

from __future__ import annotations

import pytest

from scrapemend.llm import LLMClient


def test_core_import_does_not_require_sdk():
    import scrapemend  # noqa: F401
    from scrapemend.providers import deepseek_client  # noqa: F401


def test_missing_key_raises_before_any_call(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    from scrapemend.providers.deepseek_client import DeepSeekClient

    with pytest.raises(ValueError, match="No API key"):
        DeepSeekClient()


def test_defaults_point_at_deepseek(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-not-real")
    from scrapemend.providers.deepseek_client import (
        DEEPSEEK_BASE_URL,
        DEEPSEEK_DEFAULT_MODEL,
        DeepSeekClient,
    )

    try:
        client = DeepSeekClient()
    except ImportError:
        pytest.skip("openai package not installed in this environment")

    assert isinstance(client, LLMClient)
    assert client.model == DEEPSEEK_DEFAULT_MODEL == "deepseek-chat"
    assert DEEPSEEK_BASE_URL == "https://api.deepseek.com"
    assert client.usage.total == 0
