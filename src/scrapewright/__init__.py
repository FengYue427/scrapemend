"""scrapewright — self-healing web scraping for Python.

Describe the data you want once. scrapewright extracts it with cached
selectors; when a site changes its markup and those selectors stop
matching, a language model inspects the new page and repairs them
automatically, then caches the fix so the next run is free again.
"""

from scrapewright.result import ExtractionResult
from scrapewright.schema import Field, Schema
from scrapewright.scraper import Scraper

__all__ = ["ExtractionResult", "Field", "Schema", "Scraper"]
__version__ = "0.0.1"
