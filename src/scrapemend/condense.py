"""Shrink HTML before it goes into a healing prompt.

The model only needs the page's *structure* to pick CSS selectors, not
its scripts, styles, or inline data payloads. Stripping those cuts prompt
tokens sharply (cheaper healing) and removes noise that can mislead the
model (more accurate selectors). This directly serves the library's
"robust but cheap" promise.
"""

from __future__ import annotations

import re

from selectolax.lexbor import LexborHTMLParser

#: Tags that carry no structural signal for selector discovery.
_DROP_TAGS = ("script", "style", "noscript", "template", "svg", "iframe")

#: The only attributes that matter for building CSS selectors.
_KEEP_ATTRS = ("class", "id")

_WS = re.compile(r"\s+")


def condense(html: str, limit: int = 6000) -> str:
    """Return a stripped-down version of ``html`` for prompting.

    Removes non-structural tags, drops every attribute except class/id,
    collapses whitespace, and finally caps length as a hard token guard.

    Falls back to a plain truncation if parsing fails for any reason, so
    healing never breaks just because a page is malformed.
    """
    try:
        tree = LexborHTMLParser(html)
    except Exception:  # noqa: BLE001  # pragma: no cover - last-resort guard; never let healing crash on a weird page
        return _WS.sub(" ", html)[:limit]

    for tag in _DROP_TAGS:
        for node in tree.css(tag):
            node.decompose()

    body = tree.body if tree.body is not None else tree.root
    if body is None:
        return _WS.sub(" ", html)[:limit]

    for node in body.traverse(include_text=False):
        attrs = getattr(node, "attributes", None)
        if not attrs:
            continue
        for name in list(attrs.keys()):
            if name not in _KEEP_ATTRS:
                try:
                    del node.attrs[name]
                except (KeyError, TypeError):  # pragma: no cover - defensive
                    pass

    cleaned = body.html or ""
    cleaned = _WS.sub(" ", cleaned).strip()
    return cleaned[:limit]
