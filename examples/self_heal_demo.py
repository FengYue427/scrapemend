"""Live self-healing demo using DeepSeek.

Run it to watch scrapemend survive a site "redesign": the first page
teaches it selectors, a cached run costs nothing, then the markup changes
and the LLM repairs the selectors automatically.

Setup:
    pip install "scrapemend[openai]"
    set DEEPSEEK_API_KEY=sk-...        # PowerShell: $env:DEEPSEEK_API_KEY="sk-..."
    python examples/self_heal_demo.py

No key? The script falls back to an offline stub so it still runs end to
end (with canned selectors) and you can see the flow without spending a cent.
"""

from __future__ import annotations

import os

from scrapemend import Schema, Scraper
from scrapemend.cache import SelectorCache
from scrapemend.llm import EchoClient

URL = "https://shop.demo/product/42"

# Version 1 of the page.
PAGE_V1 = """
<html><body>
  <h1 class="title">Mechanical Keyboard</h1>
  <span class="price">$89.00</span>
  <div class="stock">In stock</div>
</body></html>
"""

# Same product, redesigned markup — every selector from V1 now misses.
PAGE_V2 = """
<html><body>
  <div class="product__name">Mechanical Keyboard</div>
  <div class="product__price">$89.00</div>
  <span class="product__availability">In stock</span>
</body></html>
"""


def build_client():
    """Prefer real DeepSeek healing; fall back to an offline stub."""
    if os.environ.get("DEEPSEEK_API_KEY"):
        from scrapemend.providers.deepseek_client import DeepSeekClient

        print(">> Using DeepSeek for live healing.\n")
        return DeepSeekClient()

    print(">> No DEEPSEEK_API_KEY found — running offline with a stub.\n")
    # The stub returns whatever we set as .reply; the demo updates it to
    # mimic what a model would return for each page version.
    return EchoClient()


def main() -> None:
    schema = (
        Schema("product")
        .add("title", "the product name / title")
        .add("price", "the product price including the currency symbol")
        .add("stock", "the availability or stock status text")
    )

    client = build_client()
    offline = isinstance(client, EchoClient)
    scraper = Scraper(client=client, cache=SelectorCache(".demo-cache.json"))

    print("=" * 60)
    print("Run 1 — first ever visit (no cache). Expect: HEAL.")
    if offline:
        client.reply = '{"title":"h1.title","price":"span.price","stock":"div.stock"}'
    r1 = scraper.extract(URL, schema, html=PAGE_V1)
    _report(r1)

    print("=" * 60)
    print("Run 2 — same markup again. Expect: CACHE HIT, 0 tokens.")
    r2 = scraper.extract(URL, schema, html=PAGE_V1)
    _report(r2)

    print("=" * 60)
    print("Run 3 — the site got redesigned (new markup). Expect: RE-HEAL.")
    if offline:
        client.reply = (
            '{"title":"div.product__name","price":"div.product__price",'
            '"stock":"span.product__availability"}'
        )
    r3 = scraper.extract(URL, schema, html=PAGE_V2)
    _report(r3)

    print("=" * 60)
    print("Done. Same Schema, two different layouts, zero hand-written selectors.")


def _report(result) -> None:
    status = "CACHE HIT" if result.from_cache else ("HEALED" if result.healed else "parsed")
    print(f"  status : {status}")
    print(f"  tokens : {result.tokens}")
    print(f"  data   : {result.data}")
    if result.notes:
        print(f"  notes  : {result.notes}")
    print()


if __name__ == "__main__":
    main()
