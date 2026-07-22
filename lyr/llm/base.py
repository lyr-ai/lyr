"""LLMClient protocol — the contract every provider implements."""

from __future__ import annotations

from typing import Protocol


class LLMClient(Protocol):
    """Anything that maps a prompt string to a completion string.

    Kept deliberately narrow: the semantic builder only needs text in, text out.
    This keeps LYR's dependency on any particular SDK behind one seam and makes
    the LLM path trivially fakeable in tests (see ``FakeClient``).
    """

    def complete(self, prompt: str) -> str: ...
