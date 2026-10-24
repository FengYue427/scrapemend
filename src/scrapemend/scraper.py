"""The public entry point tying cache, parsing, and healing together.

Flow per extraction:
    1. Try cached selectors (free, fast).
    2. If any required field fails to match, the page likely changed —
       invoke the LLM healer, re-extract, and cache the repaired selectors.

This "cache first, heal only on miss" policy is the whole point: you get
AI robustness without paying an LLM call on every request.
"""

from __future__ import annotations

import httpx
from selectolax.lexbor import LexborHTMLParser as HTMLParser

from scrapemend.cache import SelectorCache
from scrapemend.healer import heal
from scrapemend.llm import EchoClient, LLMClient
from scrapemend.result import ExtractionResult
from scrapemend.schema import Schema
from scrapemend.validate import field_is_plausible


class Scraper:
    """Extracts data described by a :class:`Schema` from web pages.

    Args:
        client: LLM adapter used for healing. Defaults to an offline stub
            so the library imports and runs without any API key; pass a
            real provider adapter to enable actual healing.
        cache: Selector cache. Defaults to a JSON file in the cwd.
    """

    def __init__(self, client: LLMClient | None = None, cache: SelectorCache | None = None) -> None:
        self.client = client or EchoClient()
        self.cache = cache or SelectorCache()

    def fetch(self, url: str) -> str:
        resp = httpx.get(url, follow_redirects=True, timeout=30)
        resp.raise_for_status()
        return resp.text

    def extract(self, url: str, schema: Schema, *, html: str | None = None) -> ExtractionResult:
        """Extract ``schema`` from ``url`` (or supplied ``html``)."""
        page = html if html is not None else self.fetch(url)
        tree = HTMLParser(page)

        selectors = self.cache.get(schema.name, url)
        if selectors is not None:
            result = self._apply(tree, schema, selectors)
            if not result.notes:  # every field matched AND passed validation
                result.from_cache = True
                return result
            # Cached selectors went stale (missed or produced bad values) —
            # fall through to healing.

        return self._heal_and_extract(url, schema, page, tree)

    def _heal_and_extract(
        self, url: str, schema: Schema, page: str, tree: HTMLParser
    ) -> ExtractionResult:
        before = self.client.usage.total
        selectors = heal(schema, page, self.client)
        spent = self.client.usage.total - before

        if not selectors:
            return ExtractionResult(
                from_cache=False,
                healed=True,
                tokens=spent,
                notes=["healing failed: model returned no usable selectors"],
            )

        result = self._apply(tree, schema, selectors)
        result.from_cache = False
        result.healed = True
        result.tokens = spent
        # Only cache selectors that produced a clean extraction: every field
        # matched, had sane cardinality, and passed validation. Caching a
        # partial/implausible result would reintroduce silent-wrong-data.
        if not result.notes:
            self.cache.put(schema.name, url, selectors)
        return result

    @staticmethod
    def _apply(tree: HTMLParser, schema: Schema, selectors: dict[str, str]) -> ExtractionResult:
        out = ExtractionResult()
        for f in schema.fields:
            sel = selectors.get(f.name)
            nodes = tree.css(sel) if sel else []
            if not nodes:
                out.notes.append(f"{f.name}: no match")
                out.data[f.name] = [] if f.many else None
                continue

            # Cardinality guard: a single-value field whose selector now hits
            # several nodes is suspicious (classic "related products" drift).
            if not f.many and len(nodes) > 1:
                out.notes.append(f"{f.name}: expected one node, matched {len(nodes)}")

            values = [_read(n, f.attr) for n in nodes]
            value = values if f.many else values[0]
            out.data[f.name] = value

            # Content guard: matched, but does the value look right?
            if not field_is_plausible(f, value):
                out.notes.append(f"{f.name}: value failed validation")
        return out


def _read(node, attr: str | None) -> str:
    if attr is not None:
        return node.attributes.get(attr, "") or ""
    return node.text(strip=True)
