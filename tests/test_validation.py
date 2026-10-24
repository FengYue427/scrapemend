"""The 'matched but wrong node' failure — validation must catch it.

A redesign can leave an old selector still matching, but pointing at the
wrong element (a struck-through old price, or the first item in a related
rail). A pure match/no-match test would hit the cache and return wrong
data for free. These tests pin down that validation turns that case into
a miss that triggers healing. All offline via EchoClient.
"""

from __future__ import annotations

from scrapemend import Schema, Scraper
from scrapemend.cache import SelectorCache
from scrapemend.llm import EchoClient
from scrapemend.schema import Field
from scrapemend.validate import field_is_plausible

# --- unit level: field_is_plausible -------------------------------------

def test_number_rule_rejects_non_numeric():
    f = Field("price", "the price", expect="number")
    assert field_is_plausible(f, "$19.99") is True
    assert field_is_plausible(f, "Save on shipping") is False  # matched wrong node


def test_nonempty_rule_rejects_blank():
    f = Field("title", "the title", expect="nonempty")
    assert field_is_plausible(f, "Wireless Mouse") is True
    assert field_is_plausible(f, "   ") is False


def test_single_field_missing_value_is_implausible():
    f = Field("title", "the title")
    assert field_is_plausible(f, None) is False


def test_callable_rule():
    f = Field("sku", "the sku", expect=lambda v: v.startswith("SKU-"))
    assert field_is_plausible(f, "SKU-42") is True
    assert field_is_plausible(f, "42") is False


# --- pipeline level: cache serves good data, re-heals on bad ------------

GOOD = """
<html><body>
  <h1 class="title">Wireless Mouse</h1>
  <span class="price">$19.99</span>
</body></html>
"""

# Selector still matches `.price`, but after a "redesign" it now lands on a
# non-numeric label — the matched-but-wrong case.
WRONG = """
<html><body>
  <h1 class="title">Wireless Mouse</h1>
  <span class="price">Free shipping today</span>
</body></html>
"""


def _schema() -> Schema:
    return (
        Schema("product")
        .add("title", "the product name")
        .add("price", "the product price with currency", expect="number")
    )


def test_validation_forces_reheal_on_matched_but_wrong(tmp_path):
    cache = SelectorCache(tmp_path / "cache.json")
    client = EchoClient(reply='{"title": "h1.title", "price": "span.price"}')
    scraper = Scraper(client=client, cache=cache)

    # Learn selectors on a good page; price is numeric -> clean cache.
    r1 = scraper.extract("https://shop.example/p/1", _schema(), html=GOOD)
    assert r1["price"] == "$19.99"
    assert r1.notes == []

    # Same selectors would still *match* on WRONG, but the value isn't a
    # number. Validation must flag it and re-heal instead of serving garbage.
    tokens_before = client.usage.total
    r2 = scraper.extract("https://shop.example/p/1", _schema(), html=WRONG)
    assert r2.healed is True
    assert r2.from_cache is False
    assert client.usage.total > tokens_before  # the model was actually called


def test_cardinality_guard_flags_single_field_matching_many(tmp_path):
    cache = SelectorCache(tmp_path / "cache.json")
    # Selector ".item" is fine on a one-item page...
    one = '<html><body><div class="item">10</div></body></html>'
    many = (
        '<html><body><div class="item">10</div>'
        '<div class="item">20</div><div class="item">30</div></body></html>'
    )
    client = EchoClient(reply='{"qty": ".item"}')
    schema = Schema("x").add("qty", "the quantity", expect="number")
    scraper = Scraper(client=client, cache=cache)

    r1 = scraper.extract("https://s.example/i", schema, html=one)
    assert r1.notes == []

    # On the many-node page the single-value selector drifts to 3 matches;
    # the cardinality guard should mark it stale and trigger healing.
    r2 = scraper.extract("https://s.example/i", schema, html=many)
    assert r2.healed is True
