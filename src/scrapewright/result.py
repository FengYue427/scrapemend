"""Return type carrying extracted data plus a little provenance.

Beyond the data itself, each extraction reports *how* it was produced:
whether cached selectors worked or the LLM had to heal them, and the
token cost of any healing. That provenance is what later powers cost
tracking — the shared layer the planned LLM-tooling product reuses.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExtractionResult:
    """Outcome of a single extraction.

    Attributes:
        data: Mapping of field name to extracted value(s).
        healed: True when selectors had to be repaired by the LLM this run.
        from_cache: True when every field was served from cached selectors.
        tokens: Tokens spent on healing this run (0 when nothing healed).
        notes: Human-readable diagnostics, e.g. which fields failed.
    """

    data: dict[str, Any] = field(default_factory=dict)
    healed: bool = False
    from_cache: bool = True
    tokens: int = 0
    notes: list[str] = field(default_factory=list)

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)
