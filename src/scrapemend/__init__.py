"""scrapemend — self-healing web scraping for Python.

Describe the data you want once. scrapemend extracts it with cached
selectors; when a site changes its markup and those selectors stop
matching, a language model inspects the new page and repairs them
automatically, then caches the fix so the next run is free again.
"""

from scrapemend.result import ExtractionResult
from scrapemend.schema import Field, Schema
from scrapemend.scraper import Scraper

__all__ = ["ExtractionResult", "Field", "Schema", "Scraper"]
__version__ = "0.0.1"
