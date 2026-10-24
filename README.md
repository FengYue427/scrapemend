# scrapewright

**Self-healing web scraping for Python.** Describe the data you want once.
scrapewright extracts it with cached CSS selectors — and when a site changes
its markup and those selectors break, a language model inspects the new page,
repairs the selectors, and caches the fix. The next run is free again.

> Traditional scrapers break every time a site is redesigned. scrapewright
> treats a broken selector as a cache miss, not a crash.

---

## Why

Every scraper hits the same wall: you write selectors, the site ships a
redesign, your selectors silently return nothing, and you go rewrite them by
hand. Cloud "AI scraping" services solve the robustness problem but are
expensive, send your target data through someone else's servers, and run an
LLM call on *every* request.

scrapewright takes the middle path:

- **Cache first.** Known selectors run with zero LLM cost — it's just parsing.
- **Heal on miss.** The LLM is only called when selectors stop matching.
- **Self-hosted.** It's a library, not a service. Your keys, your data.

## Install

```bash
pip install scrapewright
```

## Quickstart

```python
from scrapewright import Scraper, Schema

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
selector — scrapewright discovers them, and re-discovers them when they break.

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

## Status

Early alpha (`0.0.1`). The core pipeline — cache, parse, heal, re-cache — works
and is covered by tests that run fully offline. A real OpenAI adapter is the
next step; the LLM layer is provider-agnostic by design.

## Roadmap

- [x] Cache-first / heal-on-miss pipeline
- [x] Offline, key-free test path
- [ ] OpenAI adapter
- [ ] Local-model adapter
- [ ] HTML condensing for cheaper prompts
- [ ] Pluggable cost/budget guards

## License

MIT
