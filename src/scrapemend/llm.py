"""The shared LLM layer.

This module is deliberately generic: a provider-agnostic client plus a
token/cost ledger. scrapemend uses it only for selector healing, but it
carries no scraping concepts, so the planned LLM-developer-tooling product
can reuse it wholesale. Keep it free of any scraping imports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass
class Usage:
    """Running tally of tokens spent, so callers can report real cost."""

    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    def add(self, prompt: int, completion: int) -> None:
        self.prompt_tokens += prompt
        self.completion_tokens += completion


@runtime_checkable
class LLMClient(Protocol):
    """Minimal contract any provider adapter must satisfy.

    Kept tiny on purpose: one text-in/text-out call. Concrete adapters
    (OpenAI, local models, etc.) live in submodules and record usage.
    """

    usage: Usage

    def complete(self, system: str, user: str) -> str:
        """Return the model's text response to a system+user prompt."""
        ...


@dataclass
class EchoClient:
    """A no-network stub used in tests and offline development.

    It never contacts a provider; it just returns a fixed string. This
    lets the whole heal/extract pipeline run in CI without API keys.
    """

    reply: str = "{}"
    usage: Usage = field(default_factory=Usage)

    def complete(self, system: str, user: str) -> str:
        # Pretend we spent a few tokens so cost tracking has something to show.
        self.usage.add(prompt=len(user) // 4, completion=len(self.reply) // 4)
        return self.reply
