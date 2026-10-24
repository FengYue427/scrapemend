"""User-facing description of *what* to extract.

A ``Schema`` is a plain, declarative description of the fields the user
wants off a page. It carries no selectors — selectors are discovered and
healed at runtime and live in the cache, not here. This keeps the thing
the user writes stable even as target sites change their markup.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class Field:
    """One piece of data to pull off a page.

    Args:
        name: Key the extracted value appears under in the result.
        describe: Plain-language description used by the LLM to locate the
            value when selectors need to be (re)discovered. Example:
            "the product price including currency symbol".
        many: If True, collect every match as a list instead of the first.
        attr: Optional HTML attribute to read (e.g. "href"). When None, the
            element's text content is used.
        expect: Optional sanity check on the extracted value. A cached
            selector that still *matches* but yields an implausible value
            (e.g. a price that no longer parses as a number) is treated as
            a miss and triggers healing — this catches the "matched but
            wrong node" failure that a pure match/no-match test misses.
            Built-in rules: ``"number"`` (value must contain a number),
            ``"nonempty"`` (value must be non-empty text). You may also pass
            a callable ``str -> bool``.
    """

    name: str
    describe: str
    many: bool = False
    attr: str | None = None
    expect: str | Callable[[str], bool] | None = None


@dataclass
class Schema:
    """A named collection of :class:`Field` objects.

    The ``name`` is used as the cache namespace so that selectors healed
    for one schema/site pair do not collide with another.
    """

    name: str
    fields: list[Field] = field(default_factory=list)

    def add(
        self,
        name: str,
        describe: str,
        *,
        many: bool = False,
        attr: str | None = None,
        expect: str | Callable[[str], bool] | None = None,
    ) -> Schema:
        """Add a field and return self so calls can be chained."""
        self.fields.append(
            Field(name=name, describe=describe, many=many, attr=attr, expect=expect)
        )
        return self

    def field_names(self) -> list[str]:
        return [f.name for f in self.fields]
