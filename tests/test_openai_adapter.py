"""Structural tests for the OpenAI adapter — no network, no spend.

We never call the real API here. We only verify that the adapter obeys
the LLMClient protocol and fails loudly and early when misconfigured.
"""

from __future__ import annotations

import pytest

from scrapemend.llm import LLMClient


def test_importing_scrapemend_does_not_require_openai():
    # Core import must stay dependency-light; adapter import is separate.
    import scrapemend  # noqa: F401
    from scrapemend.providers import openai_client  # noqa: F401


def test_missing_key_raises_before_any_call(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    from scrapemend.providers.openai_client import OpenAIClient

    with pytest.raises(ValueError, match="No API key"):
        OpenAIClient()


def test_adapter_satisfies_protocol_shape(monkeypatch):
    # With a key present, construction should wire up a usage ledger and a
    # complete() method, matching the structural LLMClient protocol.
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-not-real")
    from scrapemend.providers.openai_client import OpenAIClient

    try:
        client = OpenAIClient()
    except ImportError:
        pytest.skip("openai package not installed in this environment")

    assert isinstance(client, LLMClient)  # runtime_checkable protocol
    assert client.usage.total == 0
    assert hasattr(client, "complete")
