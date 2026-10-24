"""DeepSeek-backed adapter for selector healing.

DeepSeek exposes an OpenAI-compatible API, so this adapter reuses the
``openai`` SDK and only swaps the base URL, key source, and model name.
It supports JSON output mode, which is exactly what the healer wants
(a strict JSON object mapping fields to selectors).

DeepSeek is a strong default here: it is reachable from mainland China
without extra setup and is cheap enough that infrequent healing calls
are effectively free. Install the SDK with:

    pip install "scrapemend[openai]"

and set DEEPSEEK_API_KEY in your environment.
"""

from __future__ import annotations

import os

from scrapemend.llm import Usage

#: DeepSeek's OpenAI-compatible endpoint.
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

#: Alias that always points at DeepSeek's current main chat model, so this
#: adapter keeps working across model version bumps.
DEEPSEEK_DEFAULT_MODEL = "deepseek-chat"


class DeepSeekClient:
    """Calls DeepSeek's chat API (OpenAI-compatible) and tracks usage.

    Args:
        model: Chat model name. Defaults to the ``deepseek-chat`` alias.
        api_key: Overrides the ``DEEPSEEK_API_KEY`` environment variable.
        base_url: Overrides the default DeepSeek endpoint (useful for
            proxies or OpenAI-compatible gateways).
        temperature: Kept low for deterministic, parseable selector JSON.
    """

    def __init__(
        self,
        model: str = DEEPSEEK_DEFAULT_MODEL,
        api_key: str | None = None,
        base_url: str = DEEPSEEK_BASE_URL,
        temperature: float = 0.0,
    ) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - import guard
            raise ImportError(
                "The DeepSeek adapter uses the OpenAI SDK. "
                'Install it with: pip install "scrapemend[openai]"'
            ) from exc

        key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not key:
            raise ValueError(
                "No API key. Pass api_key=... or set DEEPSEEK_API_KEY in the environment."
            )

        self._client = OpenAI(api_key=key, base_url=base_url)
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
