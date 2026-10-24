"""Concrete LLM provider adapters.

Each adapter implements the :class:`scrapemend.llm.LLMClient` protocol
(a ``usage`` ledger plus a ``complete(system, user)`` call) and is kept
import-light so the core library never hard-depends on any one provider.
"""
