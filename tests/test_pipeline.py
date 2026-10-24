"""End-to-end check of the cache-first / heal-on-miss flow.

Uses the offline EchoClient so the whole pipeline runs with no network
and no API key — the same way CI will run it.
"""

from __future__ import annotations

from scrapewright import Schema, Scraper
from scrapewright.cache import SelectorCache
from scrapewright.llm import EchoClient

PAGE_V1 = """
<html><body>
  <h1 class="title">Wireless Mouse</h1>
  <span class="price">$19.99</span>
</body></html>
"""

# Same data, different markup — simulates the site getting redesigned.
PAGE_V2 = """
<html><body>
  <div class="product-name">Wireless Mouse</div>
  <div class="cost">$19.99</div>
</body></html>
"""


def _schema() -> Schema:
    return (
        Schema("product")
        .add("title", "the product name")
        .add("price", "the product price with currency")
    )


def test_heal_then_cache_then_reheal(tmp_path):
    cache = SelectorCache(tmp_path / "cache.json")

    # First run: no cache -> heal. Model "discovers" v1 selectors.
    client = EchoClient(reply='{"title": "h1.title", "price": "span.price"}')
    scraper = Scraper(client=client, cache=cache)

    r1 = scraper.extract("https://shop.example/p/1", _schema(), html=PAGE_V1)
    assert r1.healed is True
    assert r1.from_cache is False
    assert r1["title"] == "Wireless Mouse"
    assert r1["price"] == "$19.99"
    assert r1.tokens > 0

    # Second run on the SAME markup: cached selectors work, no healing.
    r2 = scraper.extract("https://shop.example/p/1", _schema(), html=PAGE_V1)
    assert r2.from_cache is True
    assert r2.healed is False
    assert r2.tokens == 0
    assert r2["title"] == "Wireless Mouse"

    # Site redesigns (PAGE_V2). Cached selectors miss -> heal again.
    client.reply = '{"title": "div.product-name", "price": "div.cost"}'
    r3 = scraper.extract("https://shop.example/p/1", _schema(), html=PAGE_V2)
    assert r3.healed is True
    assert r3.from_cache is False
    assert r3["title"] == "Wireless Mouse"
    assert r3["price"] == "$19.99"


def test_healing_failure_is_graceful():
    # Model returns junk; pipeline should not crash, just report it.
    scraper = Scraper(client=EchoClient(reply="not json"))
    r = scraper.extract("https://x.example", _schema(), html=PAGE_V1)
    assert r.healed is True
    assert "healing failed" in r.notes[0]
