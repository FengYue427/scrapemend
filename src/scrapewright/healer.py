"""Selector discovery/repair via the LLM.

Given a page and a schema, ask the model for one CSS selector per field.
The healer is only invoked when cached selectors are missing or have
stopped matching, so its token cost is paid rarely, not per request.
"""

from __future__ import annotations

import json

from scrapewright.condense import condense
from scrapewright.llm import LLMClient
from scrapewright.schema import Schema

_SYSTEM = (
    "You map data fields to CSS selectors for a web page. "
    "Return ONLY a JSON object mapping each field name to a single CSS "
    "selector string that selects the element holding that field's value. "
    "No prose, no code fences."
)


def build_prompt(schema: Schema, html: str) -> str:
    lines = [f"- {f.name}: {f.describe}" for f in schema.fields]
    return (
        "Fields to locate:\n"
        + "\n".join(lines)
        + "\n\nPage HTML (condensed, possibly truncated):\n"
        + condense(html)
    )


def heal(schema: Schema, html: str, client: LLMClient) -> dict[str, str]:
    """Ask the LLM for fresh selectors. Returns {field_name: selector}.

    Unknown or malformed replies yield an empty mapping rather than
    raising, so the caller can record a clean failure and move on.
    """
    reply = client.complete(_SYSTEM, build_prompt(schema, html))
    try:
        parsed = json.loads(reply)
    except json.JSONDecodeError:
        return {}
    if not isinstance(parsed, dict):
        return {}
    # Keep only known fields with string selectors.
    valid = set(schema.field_names())
    return {k: v for k, v in parsed.items() if k in valid and isinstance(v, str)}
