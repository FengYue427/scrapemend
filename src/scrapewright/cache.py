"""On-disk selector cache keyed by (schema, site).

The cache is what makes the common path free: once selectors are known
for a given schema and host, extraction is pure parsing with no LLM call.
Healing only writes here when the cached selectors stop matching.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse


class SelectorCache:
    """Maps a schema+host to the CSS selectors last known to work.

    Stored as a single JSON file so it is trivial to inspect, diff, and
    commit to a repo if a team wants to share healed selectors. (Shared,
    hosted cache sync is a candidate Pro feature later.)
    """

    def __init__(self, path: str | Path = ".scrapewright-cache.json") -> None:
        self.path = Path(path)
        self._data: dict[str, dict[str, str]] = {}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self._data = {}

    def _flush(self) -> None:
        self.path.write_text(
            json.dumps(self._data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    @staticmethod
    def _key(schema_name: str, url: str) -> str:
        host = urlparse(url).netloc or "unknown"
        return f"{schema_name}@{host}"

    def get(self, schema_name: str, url: str) -> dict[str, str] | None:
        """Return cached {field_name: css_selector} or None if unknown."""
        return self._data.get(self._key(schema_name, url))

    def put(self, schema_name: str, url: str, selectors: dict[str, str]) -> None:
        """Store healed selectors for this schema+host and persist."""
        self._data[self._key(schema_name, url)] = selectors
        self._flush()

    def drop(self, schema_name: str, url: str) -> None:
        """Forget selectors for a schema+host (forces a re-heal next run)."""
        self._data.pop(self._key(schema_name, url), None)
        self._flush()
