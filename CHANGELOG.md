# Changelog

All notable changes to scrapemend are documented here.
This project follows [Semantic Versioning](https://semver.org/).

## [0.0.2]

### Added
- **Value validation to catch the "matched but wrong node" failure.** After a
  redesign an old selector can still *match* but point at the wrong element
  (a struck-through "was" price, the first card in a related rail), so every
  field matches, the cache hits, and wrong data is returned for free. Fields
  now accept an `expect` rule (`"number"`, `"nonempty"`, or a `str -> bool`
  callable); a matched value that fails its check counts as a miss and triggers
  healing.
- **Cardinality guard.** A single-value field whose selector suddenly matches
  several nodes is treated as stale and re-healed.
- Caching tightened: only clean extractions (all fields matched, sane
  cardinality, validation passed) are written to the selector cache.

### Thanks
- Validation design prompted by community feedback on the launch post. The
  "matched but wrong node" case was the right thing to guard first.

## [0.0.1]

### Added
- Initial release: cache-first / heal-on-miss scraping pipeline.
- Offline stub client (runs with no API key) plus OpenAI and DeepSeek adapters.
- HTML condensing before healing to keep prompts small and cheap.
- Fully offline test suite and CI.
