"""OpenAI-backed adapter for selector healing.

Implements the LLMClient protocol. The ``openai`` package is imported
lazily so that merely importing scrapewright never requires it — only
constructing an :class:`OpenAIClient` does. Install with:

    pip install "scrapewright[openai]"
"""

from __future__ import annotations

import os

from scrapewright.llm import Usage


class OpenAIClient:
    """Calls an OpenAI chat model and tracks token usage.

    Args:
        model: Chat model name. A small, cheap model is the sensible
            default since healing is infrequent and the task is narrow.
        api_key: Overrides the ``OPENAI_API_KEY`` environment variable.
        temperature: Kept low for deterministic, parseable selector JSON.
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        temperature: float = 0.0,
    ) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - import guard
            raise ImportError(
                "The OpenAI adapter needs the 'openai' package. "
                'Install it with: pip install "scrapewright[openai]"'
            ) from exc

        key = api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise ValueError(
                "No API key. Pass api_key=... or set OPENAI_API_KEY in the environment."
            )

        self._client = OpenAI(api_key=key)
        self.model = model
        self.temperature = temperature
        self.usage = Usage()

    def complete(self, system: str, user: str) -> str:
        resp = self._client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        if resp.usage is not None:
            self.usage.add(
                prompt=resp.usage.prompt_tokens,
                completion=resp.usage.completion_tokens,
            )
        return resp.choices[0].message.content or "{}"
