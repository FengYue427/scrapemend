# scrapemend

**Self-healing web scraping for Python.** Describe the data you want once.
scrapemend extracts it with cached CSS selectors — and when a site changes
its markup and those selectors break, a language model inspects the new page,
repairs the selectors, and caches the fix. The next run is free again.

> Traditional scrapers break every time a site is redesigned. scrapemend
> treats a broken selector as a cache miss, not a crash.

---

## Why

Every scraper hits the same wall: you write selectors, the site ships a
redesign, your selectors silently return nothing, and you go rewrite them by
hand. Cloud "AI scraping" services solve the robustness problem but are
expensive, send your target data through someone else's servers, and run an
LLM call on *every* request.

scrapemend takes the middle path:

- **Cache first.** Known selectors run with zero LLM cost — it's just parsing.
- **Heal on miss.** The LLM is only called when selectors stop matching.
- **Self-hosted.** It's a library, not a service. Your keys, your data.

## Install

```bash
pip install scrapemend
```

## Quickstart

```python
from scrapemend import Scraper, Schema

schema = (
    Schema("product")
    .add("title", "the product name")
    .add("price", "the product price with currency")
)

scraper = Scraper()  # offline stub by default; plug in a real LLM to heal
result = scraper.extract("https://shop.example/p/1", schema)

print(result["title"], result["price"])
print("healed:", result.healed, "tokens:", result.tokens)
```

You describe *what* you want in plain language. You never hand-write a CSS
selector — scrapemend discovers them, and re-discovers them when they break.

## How it works

```
extract(url, schema)
      │
      ├─ cached selectors exist? ──► apply them
      │                               ├─ all fields matched ──► return (free)
      │                               └─ some field missed ──┐
      │                                                      ▼
      └─ no cache ─────────────────────────────────► LLM heals selectors
                                                      apply, cache, return
```

Because healing only runs on a miss, steady-state scraping costs nothing in
tokens. You pay the model exactly when a site actually changes.

## Not just match/no-match

A redesign doesn't always break a selector cleanly. Sometimes the old
selector still *matches* but now points at the wrong node — a struck-through
"was" price, or the first card in a "related products" rail. Every field
matches, the cache hits, and wrong data is returned for free: the same silent
failure you were trying to avoid.

scrapemend guards against this by validating a cached extraction before
trusting it:

```python
schema = (
    Schema("product")
    .add("title", "the product name", expect="nonempty")
    .add("price", "the product price with currency", expect="number")
)
```

If a matched value fails its `expect` check (or a single-value field suddenly
matches several nodes), that counts as a miss and triggers healing — instead
of silently caching garbage. `expect` takes `"number"`, `"nonempty"`, or any
`str -> bool` callable.

## Status

Early alpha (`0.0.1`). The core pipeline — cache, parse, validate, heal,
re-cache — works and is covered by tests that run fully offline. The LLM layer
is provider-agnostic; OpenAI and DeepSeek adapters ship today.

## Roadmap

- [x] Cache-first / heal-on-miss pipeline
- [x] Offline, key-free test path
- [x] OpenAI adapter
- [x] DeepSeek adapter
- [x] HTML condensing for cheaper prompts
- [x] Value validation (catch "matched but wrong node")
- [ ] Selector fingerprinting (detect drift even when a value still passes)
- [ ] Multiple selector sets per field (survive A/B and geo variants)
- [ ] Local-model adapter
- [ ] Pluggable cost/budget guards

## License

MIT
