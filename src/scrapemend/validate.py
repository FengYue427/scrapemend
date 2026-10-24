"""Sanity-check extracted values, not just whether a selector matched.

The subtle failure a pure match/no-match test misses: after a redesign an
old selector can still *match* but point at the wrong node — a struck-through
"was" price, or the first card in a "related products" rail. Every field
matches, the cache hits, and wrong data is returned for free. That is the
same silent failure the library set out to kill.

So before trusting a cached extraction we validate each field's value. A
field that matches but fails its check counts as a miss and triggers healing.
"""

from __future__ import annotations

import re
from collections.abc import Callable

from scrapemend.schema import Field

_NUMBER = re.compile(r"\d")


def _check_value(value: str, rule: str | Callable[[str], bool]) -> bool:
    """Return True if a single extracted string satisfies ``rule``."""
    if callable(rule):
        try:
            return bool(rule(value))
        except Exception:  # noqa: BLE001 - a user predicate must never crash extraction
            return False
    if rule == "number":
        return bool(_NUMBER.search(value))
    if rule == "nonempty":
        return bool(value and value.strip())
    # Unknown rule name: don't block extraction on a typo'd rule.
    return True


def field_is_plausible(field: Field, value: object) -> bool:
    """Check an extracted field value against the field's expectations.

    Two guards, both cheap:

    1. **Cardinality.** A single-value field (``many=False``) that produced
       no value is implausible. (A ``many`` field is allowed to be empty.)
    2. **Content.** If the field declares ``expect``, every extracted string
       must satisfy it.

    Returns True when the value looks right, False when healing is warranted.
    """
    if not field.many and (value is None or (isinstance(value, str) and not value.strip())):
        return False

    if field.expect is None:
        return True

    values = value if isinstance(value, list) else [value]
    if not values:
        # An expectation was declared but nothing was captured.
        return field.many  # empty is only acceptable for list fields
    return all(isinstance(v, str) and _check_value(v, field.expect) for v in values)
